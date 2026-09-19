"""Leased shared worker. Run with `python -m clausegraph.worker`."""
import logging
import hashlib
import secrets
import time

from clausegraph.config import get_settings
from clausegraph.extraction import validate_extraction
from clausegraph.graph import build_graph
from clausegraph.providers import ProviderError, Providers
from clausegraph.schemas import ReviewStatus, Workspace
from clausegraph.storage import MissingSession, Originals, StaleRevision, Store

log = logging.getLogger("clausegraph.worker")


def run_once(store: Store, originals: Originals, providers: Providers, owner: str | None = None) -> bool:
    owner = owner or secrets.token_urlsafe(12)
    job = store.claim(owner)
    if job is None:
        return False
    document = None
    revision = None
    try:
        if not job["payload"].get("consent"):
            raise ProviderError("External processing consent is missing; no document data was sent.")
        if job["payload"].get("evidence_provider", providers.settings.evidence_provider) != providers.settings.evidence_provider:
            raise ProviderError("Evidence provider changed after consent. Re-upload with renewed consent; no document data was sent.")
        if (job["payload"].get("text_provider", "nvidia") != providers.settings.text_provider
                or job["payload"].get("processing_route", providers.settings.processing_route) != providers.settings.processing_route
                or (providers.settings.text_provider == "brev" and not job["payload"].get("processing_route"))):
            raise ProviderError("Processing route changed after consent. Re-upload with renewed consent; no document data was sent.")
        workspace = store.get(job["session_id"])
        # Read current inputs when execution begins. Any subsequent edit invalidates this result.
        revision = workspace.revision
        document = next((doc.model_copy(deep=True) for doc in workspace.documents if doc.id == job["document_id"]), None)
        if document is None:
            raise MissingSession()
        if job["payload"].get("document_version", document.version) != document.version:
            raise StaleRevision()
        vision_pages = {page.page for page in document.pages if len(page.text.strip()) < 40} if document.media_type == "application/pdf" else set()
        vision_used = bool(vision_pages) or not document.pages
        original = None
        if vision_used:
            if document.media_type != "application/pdf":
                raise ProviderError("No adequate native document text. Upload a readable text/CSV or PDF document.")
            if not store.progress(job["id"], owner, "transcribing_pages", 15):
                raise StaleRevision()
            original = originals.get(job["payload"]["original_key"])
            if hashlib.sha256(original).hexdigest() != document.sha256:
                raise ProviderError("Original integrity check failed; no extraction was performed.")
            transcribed = {page.page: page for page in providers.vision(document, original)}
            if any(number not in transcribed for number in vision_pages):
                raise ProviderError("Vision transcription omitted an unreadable source page.")
            document.pages = [transcribed[page.page] if page.page in vision_pages else page for page in document.pages]
            if not document.pages:
                document.pages = list(transcribed.values())
                vision_pages = set(transcribed)
        if not store.progress(job["id"], owner, "extracting_clauses", 30):
            raise StaleRevision()
        result = providers.extract(document, workspace.scenario)
        for rule in result.rules:
            rule.consequential = True
        result = validate_extraction(result, document)
        if not store.progress(job["id"], owner, "verifying_evidence", 65):
            raise StaleRevision()
        try:
            checks = providers.verify(document, result.rules, original)
            indexed_checks = {check.rule_id: check for check in checks}
            for rule in result.rules:
                if rule.consequential:
                    check = indexed_checks.get(rule.id)
                    attribution = f"{providers.evidence_name} ({providers.evidence_model}); model check, not proof. "
                    rule.verifier_notes = attribution + (check.reason if check else "Verifier omitted this rule; manual review required.")
                    if check is None or not check.supported:
                        rule.evidence_status = "disputed"
                        rule.review_status = ReviewStatus.unresolved
        except ProviderError as exc:
            # Keep readable candidate facts, but verification failure blocks compilation.
            for rule in result.rules:
                if rule.consequential:
                    rule.evidence_status = "disputed"
                    rule.review_status = ReviewStatus.unresolved
                    rule.verifier_notes = str(exc)
            result.warnings.append(str(exc))
        if vision_used:
            for rule in result.rules:
                if any(evidence.page in vision_pages for evidence in rule.evidence):
                    rule.evidence_status = "disputed" if rule.evidence_status != "unsupported" else "unsupported"
                    rule.review_status = ReviewStatus.unresolved
                    rule.verifier_notes = "Image-only source: model transcription requires original-page human verification. " + (rule.verifier_notes or "")
            result.warnings.append("Image-only source transcription is not independently verified native text.")
        document.status = "needs_review"
        document.error = "; ".join(result.warnings)[:1000] or None

        def apply(current: Workspace):
            current.documents = [document if item.id == document.id else item for item in current.documents]
            prior_ids = {rule.id for rule in current.rules if any(e.document_id == document.id for e in rule.evidence)}
            current.rules = [rule for rule in current.rules if rule.id not in prior_ids] + result.rules
            current.scenario.actions = [action for action in current.scenario.actions
                if not set(action.source_rule_ids).intersection(prior_ids)] + result.actions
            current.scenario.events = [event for event in current.scenario.events
                if not set(event.source_rule_ids).intersection(prior_ids) or event.direction == "expense" or event.kind == "actual"]
            current.graph = build_graph(current.scenario, current.rules, current.documents)

        store.mutate(job["session_id"], apply, expected_revision=revision,
            job_guard=(job["id"], owner), job_result=result.model_dump(mode="json"))
    except (MissingSession, StaleRevision):
        store.progress(job["id"], owner, "stale_inputs", 100, "failed",
            "Session/document or inputs changed during processing. Re-upload with consent to retry; no stale result was applied.")
    except Exception as exc:
        error = str(exc) if isinstance(exc, ProviderError) else "Document processing failed. Check server logs and retry."
        if not isinstance(exc, ProviderError):
            # No document content, provider bodies or bearer credentials are logged.
            log.error("Processing failure type=%s", type(exc).__name__)
        store.progress(job["id"], owner, "failed", 100, "failed", error[:512])
        if document is not None and revision is not None:
            try:
                def mark_failed(current: Workspace):
                    for item in current.documents:
                        if item.id == document.id:
                            item.status = "failed"
                            item.error = error
                store.mutate(job["session_id"], mark_failed, expected_revision=revision, invalidate=False)
            except (MissingSession, StaleRevision):
                pass
    return True


def main():
    logging.basicConfig(level=logging.INFO)
    settings = get_settings()
    store = Store(settings)
    store.initialize()
    originals, providers = Originals(settings), Providers(settings)
    owner = secrets.token_urlsafe(18)
    log.info("Worker started; database backend=%s", store.engine.dialect.name)
    while True:
        if not run_once(store, originals, providers, owner):
            time.sleep(settings.worker_poll_seconds)


if __name__ == "__main__":
    main()
