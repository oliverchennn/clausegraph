"""Session-private FastAPI application. All financial arithmetic stays in the engine."""
import asyncio
import hashlib
import secrets
import time
from contextlib import asynccontextmanager
from datetime import date
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
    ApprovalStatus, AudioRequest, DeleteResponse, Document, DraftRequest, DraftResponse,
    ExtractionResult, HealthResponse, IntakeRequest, JobStatus, PlanRequest, PlanResult,
    ProviderStatus, ReviewStatus, RuleReview, Scenario, SessionCreate, TranscriptResponse,
    UploadResponse, Workspace,
)
from clausegraph.storage import MissingSession, Originals, StaleRevision, Store, utcnow

bearer = HTTPBearer(auto_error=False)


def refresh_graph(workspace: Workspace):
    from clausegraph.graph import build_graph
    workspace.graph = build_graph(workspace.scenario, workspace.rules, workspace.documents)


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

    def new_workspace(session_id: str, demo: bool) -> Workspace:
        from clausegraph.schemas import DependencyGraph
        if demo:
            from clausegraph.demo import load_demo
            scenario, documents, rules = load_demo()
        else:
            scenario = Scenario(id=secrets.token_urlsafe(12), title="My emergency plan", start_date=date.today(),
                horizon_days=60, opening_balance_cents=0, events=[], actions=[])
            documents, rules = [], []
        workspace = Workspace(session_id=session_id, mode="synthetic" if demo else "live", revision=1,
            scenario=scenario, documents=documents, rules=rules, graph=DependencyGraph())
        refresh_graph(workspace)
        return workspace

    @app.get("/api/health", response_model=HealthResponse)
    def health(request: Request):
        return HealthResponse(status="ok", database=request.app.state.store.engine.dialect.name,
            storage="private-spaces" if request.app.state.settings.spaces_configured else "private-local")

    @app.post("/api/sessions", response_model=Workspace, status_code=201)
    def create_session(body: SessionCreate, request: Request):
        workspace = request.app.state.store.create(new_workspace(secrets.token_urlsafe(32), body.demo))
        return present(request, workspace)

    @app.get("/api/workspace", response_model=Workspace)
    def get_workspace(request: Request, workspace: Session):
        return present(request, workspace)

    @app.post("/api/demo/reset", response_model=Workspace)
    def reset_demo(request: Request, workspace: Session):
        data_store = request.app.state.store
        for key in data_store.original_keys(workspace.session_id):
            request.app.state.originals.delete(key)
        data_store.delete_session(workspace.session_id)
        return present(request, data_store.create(new_workspace(workspace.session_id, True)))

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
        from clausegraph.engine import optimize
        result = optimize(workspace.scenario, workspace.rules, body, revision=workspace.revision)
        request.app.state.store.mutate(workspace.session_id, lambda current: setattr(current, "plan", result),
            expected_revision=workspace.revision, invalidate=False)
        return result

    @app.post("/api/documents", response_model=UploadResponse, status_code=201)
    async def upload(request: Request, workspace: Session, file: UploadFile = File(...), consent: bool = Form(False)):
        settings = request.app.state.settings
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
            matching_jobs = [job for job in workspace.jobs if job.document_id == duplicate.id]
            active = next((job for job in matching_jobs if job.status in ("queued", "running", "completed")), None)
            if consent and active is None:
                keys = data_store.original_keys(workspace.session_id, duplicate.id)
                if keys:
                    active = data_store.enqueue(workspace.session_id, duplicate.id, workspace.revision,
                        {"consent": True, "original_key": keys[0]})
            return UploadResponse(document=duplicate, job=active, duplicate=True)
        from clausegraph.extraction import extract_native
        try:
            pages = await run_in_threadpool(extract_native, content, name, media_type)
        except Exception as exc:
            raise HTTPException(422, "The document could not be read. Check that the PDF is valid and unencrypted.") from exc
        document = Document(id=secrets.token_urlsafe(18), name=name, media_type=media_type,
            sha256=digest, pages=pages, created_at=utcnow(), synthetic=False,
            status="uploaded" if consent else "needs_review",
            error=None if consent else "External processing was not authorized. Native text was stored privately; no provider was called.")
        key = await run_in_threadpool(request.app.state.originals.put, workspace.session_id, document.id, content, media_type)
        try:
            def apply(current: Workspace):
                current.documents.append(document)
                refresh_graph(current)
            updated = data_store.mutate(workspace.session_id, apply, expected_revision=workspace.revision)
            data_store.set_original(workspace.session_id, document.id, key)
        except Exception:
            await run_in_threadpool(request.app.state.originals.delete, key)
            raise
        job = data_store.enqueue(workspace.session_id, document.id, updated.revision,
            {"consent": True, "original_key": key}) if consent else None
        return UploadResponse(document=document, job=job)

    @app.delete("/api/documents/{document_id}", response_model=Workspace)
    def delete_document(document_id: str, request: Request, workspace: Session):
        if not any(document.id == document_id for document in workspace.documents):
            raise HTTPException(404, "Document not found in this session.")
        rule_ids = {rule.id for rule in workspace.rules if any(item.document_id == document_id for item in rule.evidence)}
        keys = request.app.state.store.original_keys(workspace.session_id, document_id)
        for key in keys:
            request.app.state.originals.delete(key)
        def apply(current: Workspace):
            current.documents = [document for document in current.documents if document.id != document_id]
            current.rules = [rule for rule in current.rules if rule.id not in rule_ids]
            current.scenario.actions = [action for action in current.scenario.actions if not rule_ids.intersection(action.source_rule_ids)]
            current.scenario.events = [event for event in current.scenario.events if not rule_ids.intersection(event.source_rule_ids)]
            refresh_graph(current)
        updated = request.app.state.store.mutate(workspace.session_id, apply, expected_revision=workspace.revision)
        request.app.state.store.purge_document_history(workspace.session_id, document_id, list(rule_ids))
        updated.jobs = request.app.state.store.list_jobs(workspace.session_id)
        return present(request, updated)

    @app.patch("/api/rules/{rule_id}", response_model=Workspace)
    def review_rule(rule_id: str, body: RuleReview, request: Request, workspace: Session):
        from clausegraph.extraction import compile_rules, validate_extraction
        if not any(rule.id == rule_id for rule in workspace.rules):
            raise HTTPException(404, "Rule not found in this session.")
        candidate_payloads = request.app.state.store.extraction_candidates(workspace.session_id)
        def apply(current: Workspace):
            rule = next(item for item in current.rules if item.id == rule_id)
            original_validity = rule.evidence_status
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
            # Editing an amount/date cannot make unsupported text into supported evidence.
            if body.amount_cents is not None or body.due_date is not None:
                for document in current.documents:
                    if any(e.document_id == document.id for e in rule.evidence):
                        checked = validate_extraction(ExtractionResult(rules=[rule.model_copy(deep=True)]), document)
                        if checked.rules[0].evidence_status != "supported":
                            rule.evidence_status = checked.rules[0].evidence_status
            if original_validity in ("disputed", "unsupported"):
                rule.evidence_status = original_validity
            if body.review_status == ReviewStatus.reviewed and rule.evidence_status != "supported":
                raise HTTPException(422, "Unsupported or disputed evidence cannot be marked reviewed without verified source support.")
            rule.review_status = body.review_status
            if body.approval_status is not None:
                rule.approval_status = body.approval_status
            if body.note:
                rule.verifier_notes = (rule.verifier_notes or "") + "\nHuman review: " + body.note[:1000]
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
            # Materialize only reviewed obligations. Retain unreviewed action candidates for graph/review UI.
            for payload in candidate_payloads:
                candidate = ExtractionResult.model_validate(payload)
                candidate.rules = [indexed[item.id] for item in candidate.rules if item.id in indexed]
                action_index = {item.id: item for item in current.scenario.actions}
                candidate.actions = [action_index[item.id] for item in candidate.actions if item.id in action_index]
                all_candidate_ids = {item.id for item in candidate.events}
                compiled = compile_rules(candidate)
                current.scenario.events = [item for item in current.scenario.events if item.id not in all_candidate_ids] + compiled.events
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
        for key in request.app.state.store.original_keys(workspace.session_id):
            request.app.state.originals.delete(key)
        request.app.state.store.delete_session(workspace.session_id)
        return DeleteResponse(deleted=True)

    return app


app = create_app()
