"""Session-private FastAPI application. All financial arithmetic stays in the engine."""
import asyncio
import hashlib
import json
import secrets
import time
from collections import OrderedDict
from contextlib import asynccontextmanager
from datetime import date
from threading import Lock
from typing import Annotated

from botocore.exceptions import BotoCoreError, ClientError
from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.concurrency import run_in_threadpool

from clausegraph.config import Settings, get_settings
from clausegraph.providers import ProviderError, Providers
from clausegraph.schemas import (
    ApprovalStatus, AudioRequest, CashGapDiagnostic, CashGapRequest, DeleteResponse, Document, DraftRequest, DraftResponse,
    ExtractionResult, HealthResponse, IntakeRequest, JobStatus, PlanRequest, PlanResult,
    ProviderStatus, ReviewQueue, ReviewStatus, RuleReview, Scenario, SessionCreate, TranscriptResponse,
    SynthesisAdoptionResult, SynthesisAdoptRequest, SynthesisRequest, SynthesisResult,
    UploadResponse, VerificationRequest, VerificationResult, Workspace,
)
from clausegraph.storage import MissingSession, Originals, StaleRevision, Store, utcnow

bearer = HTTPBearer(auto_error=False)


class UploadLimitMiddleware:
    """Bound multipart request bytes before the parser can spool an unbounded body."""
    def __init__(self, app, max_bytes: int):
        self.app, self.max_bytes = app, max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope.get("path") not in ("/api/documents", "/api/audio/transcribe"):
            return await self.app(scope, receive, send)
        limit = self.max_bytes + 65536  # bounded multipart form/header overhead
        headers = dict(scope.get("headers", []))
        try:
            length = int(headers.get(b"content-length", b"0"))
        except ValueError:
            return await JSONResponse({"detail": "Invalid content length."}, status_code=400)(scope, receive, send)
        if length > limit:
            return await JSONResponse({"detail": "Upload request exceeds the configured size limit."}, status_code=413)(scope, receive, send)
        buffered = bytearray()
        while True:
            try:
                message = await asyncio.wait_for(receive(), timeout=30)
            except TimeoutError:
                return await JSONResponse({"detail": "Upload timed out."}, status_code=408)(scope, receive, send)
            if message["type"] == "http.disconnect":
                return
            buffered.extend(message.get("body", b""))
            if len(buffered) > limit:
                return await JSONResponse({"detail": "Upload request exceeds the configured size limit."}, status_code=413)(scope, receive, send)
            if not message.get("more_body", False):
                break
        delivered = False
        async def bounded_receive():
            nonlocal delivered
            if delivered:
                return await receive()
            delivered = True
            return {"type": "http.request", "body": bytes(buffered), "more_body": False}
        await self.app(scope, bounded_receive, send)


def refresh_graph(workspace: Workspace):
    from clausegraph.graph import build_graph
    workspace.graph = build_graph(workspace.scenario, workspace.rules, workspace.documents)


def invalidate_source(workspace: Workspace, document_id: str, *, deleted: bool = False) -> set[str]:
    rule_ids = {rule.id for rule in workspace.rules if any(item.document_id == document_id for item in rule.evidence)}
    workspace.rules = [rule for rule in workspace.rules if rule.id not in rule_ids]
    workspace.scenario.actions = [action for action in workspace.scenario.actions if not rule_ids.intersection(action.source_rule_ids)]
    retained = []
    for event in workspace.scenario.events:
        if rule_ids.intersection(event.source_rule_ids):
            if event.direction == "income" and event.kind == "projected":
                continue
            if deleted:
                event.title = "Expense awaiting source review" if event.direction == "expense" else "Recorded income awaiting source review"
        retained.append(event)
    workspace.scenario.events = retained
    return rule_ids


def create_app(settings: Settings | None = None, store: Store | None = None,
               providers: Providers | None = None, originals: Originals | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        configured = settings or get_settings()
        app.state.settings = configured
        app.state.store = store or Store(configured)
        app.state.store.initialize()
        app.state.providers = providers or Providers(configured)
        app.state.originals = originals or Originals(configured)
        app.state.provider_cache = None
        app.state.plan_cache = OrderedDict()
        app.state.plan_cache_lock = Lock()
        yield
        if store is None:
            app.state.store.engine.dispose()

    app = FastAPI(title="ClauseGraph", version="0.1.0", lifespan=lifespan,
        description="Evidence-backed emergency planning. Synthetic demo data is explicitly labeled. No execution of payments or messages.")
    # Reading configuration here creates no database, filesystem, or network side effects.
    config = settings or get_settings()
    app.add_middleware(CORSMiddleware,
        allow_origins=[origin.strip() for origin in config.cors_origins.split(",") if origin.strip()],
        allow_credentials=False, allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type"], expose_headers=["Content-Disposition"])
    app.add_middleware(UploadLimitMiddleware, max_bytes=config.max_upload_bytes)

    @app.middleware("http")
    async def privacy_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    @app.exception_handler(MissingSession)
    async def missing_session(request: Request, exc: MissingSession):
        return JSONResponse(status_code=401, content={"detail": "Session is missing or deleted. Start a new session."})

    @app.exception_handler(StaleRevision)
    async def stale_revision(request: Request, exc: StaleRevision):
        return JSONResponse(status_code=409, content={"detail": "Workspace changed while processing. Refresh and retry."})

    @app.exception_handler(ProviderError)
    async def provider_error(request: Request, exc: ProviderError):
        return JSONResponse(status_code=503, content={"detail": str(exc)})

    @app.exception_handler(BotoCoreError)
    @app.exception_handler(ClientError)
    async def storage_error(request: Request, exc: Exception):
        return JSONResponse(status_code=503, content={"detail": "Private document storage is unavailable. No public fallback was used."})

    def session(request: Request, credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]) -> Workspace:
        if credentials is None or credentials.scheme.lower() != "bearer":
            raise HTTPException(401, "A private session bearer token is required.")
        return request.app.state.store.get(credentials.credentials)

    Session = Annotated[Workspace, Depends(session)]

    def present(request: Request, workspace: Workspace) -> Workspace:
        workspace.providers = provider_statuses(request)
        return workspace

    def provider_statuses(request: Request) -> list[ProviderStatus]:
        cache = request.app.state.provider_cache
        return cache[1] if cache and time.monotonic() - cache[0] < 300 else request.app.state.providers.statuses()

    def clear_plan_cache(request: Request, session_id: str):
        with request.app.state.plan_cache_lock:
            for key in list(request.app.state.plan_cache):
                if key[0] == session_id:
                    del request.app.state.plan_cache[key]

    def incomplete_sources(workspace: Workspace) -> list[Document]:
        represented = {(source.document_id, source.version)
            for rule in workspace.rules for source in rule.evidence}
        return [document for document in workspace.documents
            if document.status in ("uploaded", "extracting", "failed")
            or (document.status != "ready" and (document.id, document.version) not in represented)]

    def solve_plan(body: PlanRequest, request: Request, workspace: Workspace) -> PlanResult:
        """Solve or reuse an immutable result; callers decide whether to persist it."""
        from clausegraph.engine import optimize
        key = (workspace.session_id, workspace.revision,
            json.dumps(body.model_dump(mode="json"), sort_keys=True))
        with request.app.state.plan_cache_lock:
            cached = request.app.state.plan_cache.get(key)
        if cached and time.monotonic() - cached[0] < 600:
            return cached[1].model_copy(deep=True)
        try:
            result = optimize(workspace.scenario, workspace.rules, body, revision=workspace.revision)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        incomplete = incomplete_sources(workspace)
        if incomplete:
            result.state = "unresolved"
            result.warnings.append("Document source processing is incomplete; amounts or obligations may be missing. "
                "Displayed cash covers recorded facts only. Resolve the upload/processing status before confirming "
                "or verifying this plan. Sources: " + ", ".join(document.name for document in incomplete))
        with request.app.state.plan_cache_lock:
            request.app.state.plan_cache[key] = (time.monotonic(), result.model_copy(deep=True))
            request.app.state.plan_cache.move_to_end(key)
            while len(request.app.state.plan_cache) > 128:
                request.app.state.plan_cache.popitem(last=False)
        return result

    def original_bytes(request: Request, workspace: Workspace, document: Document) -> bytes:
        key = request.app.state.store.original_key(workspace.session_id, document.id, document.version)
        if key:
            content = request.app.state.originals.get(key)
            if hashlib.sha256(content).hexdigest() != document.sha256:
                raise HTTPException(409, "Original integrity check failed; evidence confirmation is blocked.")
            return content
        if document.synthetic:
            # Demo text is intentionally synthetic and immutable, not a live sponsor result.
            content = "\n\n".join(page.text for page in document.pages).encode("utf-8")
            if hashlib.sha256(content).hexdigest() != document.sha256:
                raise HTTPException(409, "Synthetic source integrity check failed.")
            return content
        raise HTTPException(404, "The private original is unavailable; evidence confirmation is blocked.")

    def new_workspace(session_id: str, demo: bool, demo_variant: str = "baseline") -> Workspace:
        from clausegraph.schemas import DependencyGraph
        if demo:
            from clausegraph.demo import load_demo
            from clausegraph.resilient_demo import load_resilient_demo
            scenario, documents, rules = load_resilient_demo() if demo_variant == "resilient" else load_demo()
        else:
            scenario = Scenario(id=secrets.token_urlsafe(12), title="My emergency plan", start_date=date.today(),
                horizon_days=60, opening_balance_cents=0, events=[], actions=[])
            documents, rules = [], []
        workspace = Workspace(session_id=session_id, mode="synthetic" if demo else "live", revision=1,
            scenario=scenario, documents=documents, rules=rules, graph=DependencyGraph(), demo_variant=demo_variant)
        refresh_graph(workspace)
        return workspace

    @app.get("/api/health", response_model=HealthResponse)
    def health(request: Request):
        return HealthResponse(status="ok", database=request.app.state.store.engine.dialect.name,
            storage="private-spaces" if request.app.state.settings.spaces_configured else "private-local")

    @app.post("/api/sessions", response_model=Workspace, status_code=201)
    def create_session(body: SessionCreate, request: Request):
        workspace = request.app.state.store.create(new_workspace(secrets.token_urlsafe(32), body.demo, body.demo_variant))
        return present(request, workspace)

    @app.get("/api/workspace", response_model=Workspace)
    def get_workspace(request: Request, workspace: Session):
        return present(request, workspace)

    @app.get("/api/history", response_model=list[PlanResult])
    def scenario_history(request: Request, workspace: Session):
        return request.app.state.store.history(workspace.session_id)

    @app.get("/api/review-queue", response_model=ReviewQueue)
    def workspace_review_queue(workspace: Session):
        from clausegraph.review import review_queue

        return review_queue(workspace)

    @app.post("/api/verify", response_model=VerificationResult)
    def verify_fixed_plan(body: VerificationRequest, request: Request, workspace: Session):
        from clausegraph.verification import verify_plan
        if workspace.revision != body.revision:
            raise StaleRevision()
        if (workspace.plan is None or workspace.plan.id != body.plan_id
                or workspace.plan.revision != body.revision):
            raise HTTPException(409, "Verify the current saved plan. Calculate a plan, refresh, and retry.")
        if incomplete_sources(workspace):
            raise HTTPException(409, "Document source processing is incomplete. Resolve the upload/processing "
                "status and calculate a current plan before verification.")
        try:
            result = verify_plan(workspace.scenario, workspace.rules, workspace.plan, body)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        return request.app.state.store.save_verification(workspace.session_id, result)

    @app.post("/api/cash-gap", response_model=CashGapDiagnostic)
    def cash_gap(body: CashGapRequest, request: Request, workspace: Session):
        """Return a side-effect-free hypothetical-cash diagnostic for the saved fixed plan."""
        from clausegraph.cash_gap import diagnose_cash_gap
        if workspace.revision != body.revision:
            raise StaleRevision()
        if (workspace.plan is None or workspace.plan.id != body.plan_id
                or workspace.plan.revision != body.revision):
            raise HTTPException(409, "Diagnose the current saved plan. Calculate a plan, refresh, and retry.")
        if incomplete_sources(workspace):
            raise HTTPException(409, "Document source processing is incomplete. Resolve the upload/processing "
                "status and calculate a current plan before diagnosing a cash gap.")
        try:
            result = diagnose_cash_gap(workspace.scenario, workspace.rules, workspace.plan, body)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        # No result is persisted, so recheck identity here instead of save_verification.
        # A replacement plan can have the same input revision; deletion must also fail closed.
        current = request.app.state.store.get(workspace.session_id)
        if (current.revision != body.revision or current.plan is None
                or current.plan.id != body.plan_id or current.plan.revision != body.revision):
            raise StaleRevision()
        return result

    @app.get("/api/verifications", response_model=list[VerificationResult])
    def verification_history(request: Request, workspace: Session):
        return request.app.state.store.verifications(workspace.session_id)

    def synthesis_source(workspace: Workspace, body: SynthesisRequest):
        if (workspace.revision != body.revision or workspace.plan is None
                or workspace.plan.id != body.plan_id or workspace.plan.revision != body.revision):
            raise StaleRevision()
        if incomplete_sources(workspace):
            raise HTTPException(409, "Document source processing is incomplete. Resolve it and save a current plan before synthesis.")

    @app.post("/api/synthesis", response_model=SynthesisResult)
    def synthesis(body: SynthesisRequest, request: Request, workspace: Session):
        from clausegraph.synthesis import synthesize_plan
        synthesis_source(workspace, body)
        try:
            result = synthesize_plan(workspace.scenario, workspace.rules, workspace.plan, body)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        synthesis_source(request.app.state.store.get(workspace.session_id), body)
        return result

    @app.post("/api/synthesis/adopt", response_model=SynthesisAdoptionResult)
    def adopt_synthesis(body: SynthesisAdoptRequest, request: Request, workspace: Session):
        from clausegraph.synthesis import CandidateUnavailable, revalidate_candidate
        synthesis_source(workspace, body.synthesis_request)
        try:
            result = revalidate_candidate(workspace.scenario, workspace.rules, workspace.plan, body)
        except CandidateUnavailable as exc:
            raise HTTPException(409, str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        request.app.state.store.adopt_synthesis(workspace.session_id, body.synthesis_request.plan_id,
            result.plan, result.verification, lambda current: synthesis_source(current, body.synthesis_request))
        clear_plan_cache(request, workspace.session_id)
        return result

    @app.post("/api/demo/reset", response_model=Workspace)
    def reset_demo(request: Request, workspace: Session):
        data_store = request.app.state.store
        def apply(current: Workspace):
            for key in data_store.original_keys(current.session_id):
                request.app.state.originals.delete(key)
            fresh = new_workspace(current.session_id, True, current.demo_variant)
            current.mode, current.scenario = fresh.mode, fresh.scenario
            current.documents, current.rules, current.graph = fresh.documents, fresh.rules, fresh.graph
            current.jobs = []
        updated = data_store.mutate(workspace.session_id, apply, expected_revision=workspace.revision, reset_history=True)
        clear_plan_cache(request, workspace.session_id)
        return present(request, updated)

    @app.post("/api/intake", response_model=Workspace)
    def intake(body: IntakeRequest, request: Request, workspace: Session):
        if len({event.id for event in body.events}) != len(body.events):
            raise HTTPException(422, "Financial event IDs must be unique.")
        def apply(current: Workspace):
            current.scenario.opening_balance_cents = body.opening_balance_cents
            current.scenario.start_date = body.start_date
            current.scenario.horizon_days = body.horizon_days
            current.scenario.events = body.events
            current.scenario.essential_service_ids = body.essential_service_ids
            refresh_graph(current)
        return present(request, request.app.state.store.mutate(workspace.session_id, apply,
            expected_revision=workspace.revision))

    @app.post("/api/plan", response_model=PlanResult)
    def plan(body: PlanRequest, request: Request, workspace: Session):
        result = solve_plan(body, request, workspace)
        request.app.state.store.mutate(workspace.session_id, lambda current: setattr(current, "plan", result),
            expected_revision=workspace.revision, invalidate=False)
        return result

    @app.post("/api/plan/preview", response_model=PlanResult)
    def preview_plan(body: PlanRequest, request: Request, workspace: Session):
        """Return a side-effect-free scenario result for comparison."""
        return solve_plan(body, request, workspace)

    @app.post("/api/documents", response_model=UploadResponse, status_code=201)
    async def upload(request: Request, workspace: Session, file: UploadFile = File(...), consent: bool = Form(False),
                     consent_provider: str | None = Form(None), consent_text_provider: str | None = Form(None)):
        settings = request.app.state.settings
        if consent and (consent_text_provider != settings.text_provider
                        and (consent_text_provider is not None or settings.text_provider == "brev")):
            await file.close()
            raise HTTPException(409, "Text provider changed or Brev consent is missing. Review the processing destination before uploading.")
        if consent and consent_provider is not None and consent_provider != settings.evidence_provider:
            await file.close()
            raise HTTPException(409, "Evidence provider changed. Refresh the workspace and review processing consent again.")
        name = (file.filename or "document").replace("\\", "/").rsplit("/", 1)[-1][:180]
        extension = name.rsplit(".", 1)[-1].lower() if "." in name else ""
        types = {"pdf": "application/pdf", "txt": "text/plain", "csv": "text/csv"}
        if extension not in types:
            raise HTTPException(415, "Only PDF, UTF-8 text, and CSV documents are supported.")
        content = await file.read(settings.max_upload_bytes + 1)
        await file.close()
        if len(content) > settings.max_upload_bytes:
            raise HTTPException(413, "Document exceeds the configured upload size limit.")
        if not content:
            raise HTTPException(422, "The document is empty.")
        media_type = types[extension]
        if extension == "pdf" and not content.startswith(b"%PDF-"):
            raise HTTPException(415, "The document does not have a PDF header.")
        if extension != "pdf":
            try:
                text = content.decode("utf-8-sig")
            except UnicodeDecodeError as exc:
                raise HTTPException(415, "Text and CSV documents must use UTF-8 encoding.") from exc
            if "\x00" in text:
                raise HTTPException(415, "Binary content is not a text document.")
        if settings.spaces_configured and not consent:
            raise HTTPException(403, "Consent is required before uploading originals to private cloud storage.")
        digest = hashlib.sha256(content).hexdigest()
        data_store = request.app.state.store
        duplicate = next((doc for doc in workspace.documents if doc.sha256 == digest), None)
        if duplicate:
            matching_jobs = data_store.document_jobs(workspace.session_id, duplicate.id, duplicate.version)
            active = next((job for job in matching_jobs if job.status in ("queued", "running", "completed")), None)
            if consent and active is None:
                key = data_store.original_key(workspace.session_id, duplicate.id, duplicate.version)
                if key:
                    def retry(current: Workspace):
                        target = next(item for item in current.documents if item.id == duplicate.id)
                        target.status, target.error = "uploaded", None
                    updated = data_store.mutate(workspace.session_id, retry, expected_revision=workspace.revision,
                        enqueue={"document_id": duplicate.id, "payload": {"consent": True,
                        "original_key": key, "document_version": duplicate.version, "evidence_provider": settings.evidence_provider,
                        "text_provider": settings.text_provider, "processing_route": settings.processing_route}})
                    active = updated.jobs[0]
                    duplicate = next(item for item in updated.documents if item.id == duplicate.id)
            return UploadResponse(document=duplicate, job=active, duplicate=True)
        from clausegraph.extraction import extract_native
        try:
            pages = await run_in_threadpool(extract_native, content, name, media_type)
        except Exception as exc:
            raise HTTPException(422, "The document could not be read. Check that the PDF is valid and unencrypted.") from exc
        previous = next((doc for doc in workspace.documents if doc.name.casefold() == name.casefold() and not doc.synthetic), None)
        document = Document(id=previous.id if previous else secrets.token_urlsafe(18),
            version=previous.version + 1 if previous else 1, name=name, media_type=media_type,
            sha256=digest, pages=pages, created_at=utcnow(), synthetic=False,
            status="uploaded" if consent else "needs_review",
            error=None if consent else "External processing was not authorized. Native text was stored privately; no provider was called.")
        key = await run_in_threadpool(request.app.state.originals.put, workspace.session_id, document.id, content, media_type, document.version)
        try:
            def apply(current: Workspace):
                if previous:
                    invalidate_source(current, previous.id)
                    current.documents = [item for item in current.documents if item.id != previous.id]
                current.documents.append(document)
                refresh_graph(current)
            updated = data_store.mutate(workspace.session_id, apply, expected_revision=workspace.revision,
                original=(document.id, document.version, key), enqueue={"document_id": document.id,
                    "payload": {"consent": True, "original_key": key, "document_version": document.version,
                        "evidence_provider": settings.evidence_provider, "text_provider": settings.text_provider,
                        "processing_route": settings.processing_route}} if consent else None,
                supersede_document_id=previous.id if previous else None)
        except Exception:
            await run_in_threadpool(request.app.state.originals.delete, key)
            raise
        job = next((item for item in updated.jobs if item.document_id == document.id and item.status == "queued"), None) if consent else None
        return UploadResponse(document=document, job=job)

    @app.get("/api/documents/{document_id}/original")
    def download_original(document_id: str, request: Request, workspace: Session, version: int | None = None):
        document = next((item for item in workspace.documents if item.id == document_id), None)
        if document is None:
            raise HTTPException(404, "Document not found in this session.")
        if version is not None and version != document.version:
            payload = request.app.state.store.document_version(workspace.session_id, document_id, version)
            if payload is None:
                raise HTTPException(404, "Document version not found in this session.")
            document = Document.model_validate(payload)
        content = original_bytes(request, workspace, document)
        # Fixed attachment filename avoids untrusted filename header injection.
        suffix = {"application/pdf": "pdf", "text/plain": "txt", "text/csv": "csv"}.get(document.media_type, "bin")
        return Response(content, media_type=document.media_type,
            headers={"Content-Disposition": f'attachment; filename="source-v{document.version}.{suffix}"'})

    @app.delete("/api/documents/{document_id}", response_model=Workspace)
    def delete_document(document_id: str, request: Request, workspace: Session):
        if not any(document.id == document_id for document in workspace.documents):
            raise HTTPException(404, "Document not found in this session.")
        rule_ids = {rule.id for rule in workspace.rules if any(item.document_id == document_id for item in rule.evidence)}
        def apply(current: Workspace):
            for key in request.app.state.store.original_keys(workspace.session_id, document_id):
                request.app.state.originals.delete(key)
            current.documents = [document for document in current.documents if document.id != document_id]
            invalidate_source(current, document_id, deleted=True)
            refresh_graph(current)
        updated = request.app.state.store.mutate(workspace.session_id, apply, expected_revision=workspace.revision,
            purge_document_id=document_id, purge_rule_ids=list(rule_ids))
        clear_plan_cache(request, workspace.session_id)
        return present(request, updated)

    @app.patch("/api/rules/{rule_id}", response_model=Workspace)
    def review_rule(rule_id: str, body: RuleReview, request: Request, workspace: Session):
        from clausegraph.extraction import compile_rules, extract_native, validate_extraction
        if not any(rule.id == rule_id for rule in workspace.rules):
            raise HTTPException(404, "Rule not found in this session.")
        candidate_payloads = request.app.state.store.extraction_candidates(workspace.session_id)
        def apply(current: Workspace):
            rule = next(item for item in current.rules if item.id == rule_id)
            original_validity = rule.evidence_status
            prior_amount, prior_date = rule.amount_cents, rule.due_date
            if body.amount_cents is not None:
                rule.amount_cents = body.amount_cents
            if body.due_date is not None:
                rule.due_date = body.due_date
            if body.conditions is not None:
                expected = {(condition.fact, condition.operator, str(condition.value)) for condition in rule.conditions}
                supplied = {(condition.fact, condition.operator, str(condition.value)) for condition in body.conditions}
                if expected != supplied or len(rule.conditions) != len(body.conditions):
                    raise HTTPException(422, "Review can resolve existing conditions but cannot replace source conditions.")
                rule.conditions = body.conditions
            needs_validation = body.evidence_confirmed or body.amount_cents is not None or body.due_date is not None
            deterministic_support = True
            if needs_validation:
                documents = {item.id: item for item in current.documents}
                if not rule.evidence or any(item.document_id not in documents for item in rule.evidence):
                    deterministic_support = False
                for document_id in {item.document_id for item in rule.evidence}:
                    if document_id not in documents:
                        continue
                    document = documents[document_id].model_copy(deep=True)
                    content = original_bytes(request, current, document)
                    # Validate native evidence against the original bytes, not a cached/model page.
                    native = extract_native(content, document.name, document.media_type)
                    native_index = {page.page: page for page in native}
                    document.pages = [native_index.get(page.page, page) if len(native_index.get(page.page, page).text.strip()) >= 40
                        or document.media_type != "application/pdf" else page for page in document.pages]
                    candidate_rule = rule.model_copy(deep=True)
                    candidate_rule.evidence_status = "unchecked"
                    checked = validate_extraction(ExtractionResult(rules=[candidate_rule]), document)
                    deterministic_support = deterministic_support and checked.rules[0].evidence_status == "supported"
                if not deterministic_support:
                    rule.evidence_status = "unsupported"
                elif original_validity == "supported":
                    rule.evidence_status = "supported"
            if body.evidence_confirmed:
                if not body.note or not body.note.strip():
                    raise HTTPException(422, "Evidence confirmation requires a note describing what you checked against the original.")
                if not deterministic_support:
                    raise HTTPException(422, "Original quote, amount, date, version or entity checks failed. Confirmation cannot override unsupported provenance.")
                rule.evidence_status = "supported"
            elif original_validity in ("disputed", "unsupported"):
                rule.evidence_status = original_validity
            if body.review_status == ReviewStatus.reviewed and rule.evidence_status != "supported":
                raise HTTPException(422, "Unsupported or disputed evidence cannot be marked reviewed without verified source support.")
            rule.review_status = body.review_status
            if body.approval_status is not None:
                rule.approval_status = body.approval_status
            if body.note:
                rule.verifier_notes = (rule.verifier_notes or "") + "\nHuman review: " + body.note[:1000]
            def update_derived_event(event):
                if event.kind != "projected" or rule_id not in event.source_rule_ids:
                    return
                if body.amount_cents is not None and event.amount_cents == prior_amount:
                    event.amount_cents = rule.amount_cents
                if body.due_date is not None and event.date == prior_date:
                    event.date = rule.due_date
            for event in current.scenario.events:
                update_derived_event(event)
            indexed = {item.id: item for item in current.rules}
            for action in current.scenario.actions:
                if rule_id not in action.source_rule_ids:
                    continue
                sources = [indexed[item] for item in action.source_rule_ids if item in indexed]
                action.review_status = ReviewStatus.reviewed if sources and len(sources) == len(action.source_rule_ids) and all(
                    source.review_status == ReviewStatus.reviewed for source in sources) else ReviewStatus.pending
                approvals = {source.approval_status for source in sources}
                if ApprovalStatus.denied in approvals:
                    action.approval_status = ApprovalStatus.denied
                elif ApprovalStatus.pending in approvals:
                    action.approval_status = ApprovalStatus.pending
                elif ApprovalStatus.approved in approvals:
                    action.approval_status = ApprovalStatus.approved
                else:
                    action.approval_status = ApprovalStatus.not_required
                for effect in action.effects:
                    if effect.event:
                        update_derived_event(effect.event)
                    if body.due_date is not None and effect.date == prior_date:
                        effect.date = rule.due_date
            # Materialize only reviewed obligations. Retain unreviewed action candidates for graph/review UI.
            for payload in candidate_payloads:
                candidate = ExtractionResult.model_validate(payload)
                # Cross-document dependencies resolve against the current reviewed rule set.
                candidate.rules = list(indexed.values())
                for event in candidate.events:
                    if event.kind == "projected" and len(event.source_rule_ids) == 1:
                        source = indexed.get(event.source_rule_ids[0])
                        if source and source.amount_cents is not None and source.due_date is not None:
                            event.amount_cents, event.date = source.amount_cents, source.due_date
                action_index = {item.id: item for item in current.scenario.actions}
                candidate.actions = [action_index[item.id] for item in candidate.actions if item.id in action_index]
                all_candidate_ids = {item.id for item in candidate.events}
                compiled = compile_rules(candidate)
                # Review cannot silently erase an already recorded obligation if a clause is later disputed.
                compiled_ids = {item.id for item in compiled.events}
                current.scenario.events = [item for item in current.scenario.events
                    if item.id not in all_candidate_ids or (item.id not in compiled_ids and (item.direction == "expense" or item.kind == "actual"))] + compiled.events
            for document in current.documents:
                sources = [item for item in current.rules if any(e.document_id == document.id for e in item.evidence)]
                if sources:
                    document.status = "ready" if all(item.review_status == ReviewStatus.reviewed for item in sources) else "needs_review"
            refresh_graph(current)
        return present(request, request.app.state.store.mutate(workspace.session_id, apply, expected_revision=workspace.revision))

    @app.get("/api/jobs/{job_id}", response_model=JobStatus)
    def get_job(job_id: str, request: Request, workspace: Session):
        job = request.app.state.store.get_job(workspace.session_id, job_id)
        if job is None:
            raise HTTPException(404, "Job not found in this session.")
        return job

    @app.get("/api/jobs/{job_id}/events")
    def job_events(job_id: str, request: Request, workspace: Session):
        get_job(job_id, request, workspace)
        async def events():
            previous = None
            for _ in range(120):
                if await request.is_disconnected():
                    return
                job = request.app.state.store.get_job(workspace.session_id, job_id)
                if job is None:
                    yield 'event: deleted\ndata: {"deleted":true}\n\n'
                    return
                data = job.model_dump_json()
                if data != previous:
                    yield f"event: progress\ndata: {data}\n\n"
                    previous = data
                else:
                    yield ": keepalive\n\n"
                if job.status in ("completed", "failed"):
                    return
                await asyncio.sleep(1)
        return StreamingResponse(events(), media_type="text/event-stream", headers={"X-Accel-Buffering": "no"})

    @app.get("/api/providers", response_model=list[ProviderStatus])
    def get_providers(request: Request, workspace: Session):
        return provider_statuses(request)

    @app.post("/api/providers/smoke", response_model=list[ProviderStatus])
    def smoke_providers(request: Request, workspace: Session):
        cache = request.app.state.provider_cache
        if cache and time.monotonic() - cache[0] < 30:
            return cache[1]
        statuses = request.app.state.providers.smoke()
        postgres = next(item for item in statuses if item.name == "Tiger Data / PostgreSQL")
        postgres.detail += " Current application database connection succeeded."
        spaces = next(item for item in statuses if item.name == "DigitalOcean Spaces")
        if request.app.state.originals.client:
            try:
                request.app.state.originals.client.head_bucket(Bucket=request.app.state.settings.spaces_bucket)
                spaces.detail = "Authenticated private bucket availability check succeeded; no object was published."
            except (BotoCoreError, ClientError):
                spaces.mode = "unavailable"
                spaces.detail = "Private bucket access failed. Check endpoint, bucket and credentials."
        request.app.state.provider_cache = (time.monotonic(), statuses)
        return statuses

    @app.post("/api/actions/{action_id}/draft", response_model=DraftResponse)
    def draft_request(action_id: str, request: Request, workspace: Session, body: DraftRequest = DraftRequest()):
        action = next((item for item in workspace.scenario.actions if item.id == action_id), None)
        if action is None:
            raise HTTPException(404, "Action not found in this session.")
        rules = [item for item in workspace.rules if item.id in action.source_rule_ids]
        source_quotes = [evidence.model_dump(mode="json") for rule in rules for evidence in rule.evidence]
        draft = (f"Hello,\n\nI would like to discuss this option: {action.title}.\n\n"
            f"My records describe: {action.description}\n\nPlease confirm eligibility, the effective date, any fees, "
            "and the impact on remaining obligations in writing before I proceed.\n\nThank you.")
        if body.use_provider:
            if not body.consent:
                raise HTTPException(403, "Consent is required before sending source facts for external draft generation.")
            selected = request.app.state.settings.text_provider
            if body.consent_text_provider != selected and (body.consent_text_provider is not None or selected == "brev"):
                raise HTTPException(409, "Text provider changed or Brev consent is missing. Review the processing destination before generating a draft.")
            draft = request.app.state.providers.draft(action.title, source_quotes,
                {"description": action.description, "requested_date": action.recommended_date.isoformat()})
        return DraftResponse(action_id=action_id, subject=f"Request: {action.title}", body=draft, sent=False)

    @app.get("/api/evidence/export")
    def export_evidence(request: Request, workspace: Session):
        lines = ["# ClauseGraph evidence summary", "", f"Data mode: {workspace.mode.upper()}",
            "SYNTHETIC DEMONSTRATION — not real customer documents." if workspace.mode == "synthetic" else "Private session export.",
            f"Revision: {workspace.revision}", f"Start date: {workspace.scenario.start_date}",
            "All amounts below are integer USD cents. This export executes no actions.", ""]
        for rule in workspace.rules:
            lines += [f"## {rule.title}", f"Review: {rule.review_status.value}; approval: {rule.approval_status.value}; evidence: {rule.evidence_status}",
                f"Amount cents: {rule.amount_cents}; date: {rule.due_date}"]
            for evidence in rule.evidence:
                lines += [f"Source: {evidence.document_id} v{evidence.version}, page {evidence.page}, characters {evidence.char_start}:{evidence.char_end}",
                    *["> " + line for line in evidence.quote.splitlines()]]
            for condition in rule.conditions:
                lines.append(f"Condition: {condition.fact} {condition.operator} {condition.value}; resolved={condition.resolved}, satisfied={condition.satisfied}")
            lines.append("")
        if workspace.plan:
            lines += ["## Current calculated plan", f"State: {workspace.plan.state}; solver: {workspace.plan.solver_status}",
                f"Baseline minimum cents: {workspace.plan.baseline.minimum_balance_cents}",
                f"Proposed minimum cents: {workspace.plan.proposed.minimum_balance_cents}",
                f"Ending balance cents: {workspace.plan.proposed.ending_balance_cents}",
                f"Additional cash diagnostic cents: {workspace.plan.proposed.additional_cash_required_cents}"]
            for action in workspace.plan.actions:
                lines.append(f"- {action.order}. {action.execution_date}: {action.explanation} (conditional={action.conditional})")
            lines += ["", "Beyond-horizon obligations:"]
            for event in workspace.plan.proposed.beyond_horizon:
                lines.append(f"- {event.date}: {event.title}, {event.amount_cents} cents, {event.kind}")
        return Response("\n".join(lines), media_type="text/markdown", headers={
            "Content-Disposition": 'attachment; filename="clausegraph-evidence.md"'})

    @app.post("/api/audio/transcribe", response_model=TranscriptResponse)
    async def transcribe_audio(request: Request, workspace: Session, file: UploadFile = File(...), consent: bool = Form(False)):
        if not consent:
            raise HTTPException(403, "Consent is required before external audio transcription.")
        media_type = file.content_type or "application/octet-stream"
        if media_type not in ("audio/mpeg", "audio/mp3", "audio/wav", "audio/x-wav", "audio/webm", "audio/mp4", "audio/ogg"):
            raise HTTPException(415, "Supported audio formats: MP3, WAV, WebM, MP4, OGG.")
        content = await file.read(request.app.state.settings.max_upload_bytes + 1)
        await file.close()
        if not content or len(content) > request.app.state.settings.max_upload_bytes:
            raise HTTPException(413, "Audio is empty or exceeds the upload size limit.")
        text = await run_in_threadpool(request.app.state.providers.transcribe, content, "intake-audio", media_type)
        return TranscriptResponse(text=text, facts_confirmed=False)

    @app.post("/api/audio/checklist")
    def narrated_checklist(body: AudioRequest, request: Request, workspace: Session):
        if not body.consent:
            raise HTTPException(403, "Consent is required before sending your checklist for narration.")
        if workspace.plan is None:
            raise HTTPException(409, "Calculate a current plan before requesting its checklist.")
        text = f"ClauseGraph. This plan is {workspace.plan.state}. "
        if workspace.mode == "synthetic":
            text += "This is a synthetic demonstration. "
        text += " ".join(f"Step {item.order}, on {item.execution_date.isoformat()}. {item.explanation}" for item in workspace.plan.actions)
        if not workspace.plan.actions:
            text += "There are no eligible actions. Review the cash shortfall and unresolved evidence in your workspace."
        audio = request.app.state.providers.speak(text)
        return Response(audio, media_type="audio/mpeg")

    @app.delete("/api/session", response_model=DeleteResponse)
    def delete_private_session(request: Request, workspace: Session):
        def cleanup():
            for key in request.app.state.store.original_keys(workspace.session_id):
                request.app.state.originals.delete(key)
        request.app.state.store.delete_session(workspace.session_id, expected_revision=workspace.revision, cleanup=cleanup)
        clear_plan_cache(request, workspace.session_id)
        return DeleteResponse(deleted=True)

    return app


app = create_app()
