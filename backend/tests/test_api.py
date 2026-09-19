"""Real ASGI/storage/worker workflows; external providers use explicit mock HTTP transport."""
import json
import io
from datetime import date, timedelta

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select, update

from clausegraph.api import create_app
from clausegraph.config import Settings
from clausegraph.providers import ProviderError, Providers
from clausegraph.schemas import DocumentPage, ExtractionResult
from clausegraph.storage import (
    Originals, StaleRevision, Store, daily_balances, document_versions, financial_events, jobs,
    rule_versions, scenario_runs, sessions, utcnow,
)
from clausegraph.worker import run_once

PAYMENT_TEXT = "SYNTHETIC TEST ONLY. Payment of $123.45 is due 2026-09-28. This is an invented fixture."


def candidate(document):
    quote = document["pages"][0]["text"]
    return {
        "rules": [{"id": "payment", "title": "Fixture payment", "kind": "obligation", "evidence": [{
            "document_id": document["id"], "version": document["version"], "page": 1,
            "char_start": 0, "char_end": len(quote), "quote": quote}],
            "amount_cents": 12345, "due_date": "2026-09-28", "review_status": "reviewed",
            "approval_status": "approved", "evidence_status": "supported", "consequential": False}],
        "events": [{"id": "payment", "title": "Fixture payment", "date": "2026-09-28",
            "amount_cents": 12345, "direction": "expense", "source_rule_ids": ["payment"]}],
    }


def transport_handler(request):
    if request.url.path.endswith("/chat/completions"):
        data = json.loads(json.loads(request.content)["messages"][1]["content"])
        return httpx.Response(200, json={"choices": [{"finish_reason": "stop", "message": {
            "content": json.dumps(candidate(data["source_document"]))}}]})
    if ":generateContent" in request.url.path:
        text = json.loads(request.content)["contents"][0]["parts"][0]["text"]
        data = json.loads(text[text.index('{"source_document"'):])
        return httpx.Response(200, json={"candidates": [{"finishReason": "STOP", "content": {"parts": [{
            "text": json.dumps({"checks": [{"rule_id": rule["id"], "supported": True,
                "reason": "Mocked test verifier; no live call."} for rule in data["extracted_rules"]]})}]}}]})
    if request.url.path.endswith("/speech-to-text"):
        return httpx.Response(200, json={"text": "I have 2000 dollars. This transcript must be confirmed."})
    if "/text-to-speech/" in request.url.path:
        return httpx.Response(200, content=b"fake-test-audio", headers={"content-type": "audio/mpeg"})
    raise AssertionError(f"Unexpected test request: {request.method} {request.url.path}")


@pytest.fixture
def api(tmp_path):
    settings = Settings(_env_file=None, database_url=f"sqlite:///{tmp_path / 'test.db'}",
        local_storage_path=tmp_path / "originals", nvidia_api_key="", gemini_api_key="",
        elevenlabs_api_key="", provider_retries=0)
    store = Store(settings)
    providers = Providers(settings, transport=httpx.MockTransport(transport_handler))
    originals = Originals(settings)
    with TestClient(create_app(settings, store, providers, originals)) as client:
        yield client, store, providers, originals
    store.engine.dispose()


def start(client, demo=True):
    response = client.post("/api/sessions", json={"demo": demo})
    assert response.status_code == 201, response.text
    workspace = response.json()
    return {"Authorization": f"Bearer {workspace['session_id']}"}, workspace


def upload(client, headers, text=PAYMENT_TEXT, consent=False, name="payment.txt"):
    return client.post("/api/documents", headers=headers,
        files={"file": (name, text.encode(), "text/plain")}, data={"consent": str(consent).lower()})


def intake(client, headers):
    return client.post("/api/intake", headers=headers, json={"opening_balance_cents": 100000,
        "start_date": "2026-09-01", "events": [], "essential_service_ids": []})


def test_private_sessions_health_and_provider_truth(api):
    client, _, _, _ = api
    assert client.get("/api/health").json() == {"status": "ok", "database": "sqlite", "storage": "private-local"}
    assert client.get("/api/workspace").status_code == 401
    assert client.get("/api/workspace", headers={"Authorization": "Bearer invented"}).status_code == 401
    headers, workspace = start(client)
    assert workspace["mode"] == "synthetic"
    assert len(workspace["documents"]) == 6
    response = client.get("/api/workspace", headers=headers)
    assert response.headers["cache-control"] == "no-store"
    statuses = client.post("/api/providers/smoke", headers=headers).json()
    assert all(item["mode"] == "unavailable" for item in statuses[:3])
    assert all("missing" in item["detail"].lower() for item in statuses[:3])


def test_demo_plan_approval_invalidation_cache_and_history(api):
    client, store, _, _ = api
    headers, workspace = start(client)
    plan = client.post("/api/plan", headers=headers, json={}).json()
    assert plan["state"] == "confirmed"
    assert plan["baseline"]["minimum_balance_cents"] == -40000
    assert plan["proposed"]["minimum_balance_cents"] == 5000
    assert plan["proposed"]["ending_balance_cents"] == 50000
    assert client.post("/api/plan", headers=headers, json={}).json()["id"] == plan["id"]
    other_headers, _ = start(client)
    assert client.get("/api/history", headers=other_headers).json() == []
    assert len(client.get("/api/history", headers=headers).json()) == 1
    with store.engine.connect() as connection:
        assert connection.execute(select(func.count()).select_from(daily_balances)).scalar() == 120
        assert connection.execute(select(daily_balances.c.kind).distinct()).scalars().all() == ["projected"]
    reviewed = client.patch("/api/rules/rule-shift", headers=headers,
        json={"review_status": "reviewed", "approval_status": "denied"})
    assert reviewed.status_code == 200, reviewed.text
    assert reviewed.json()["plan"] is None
    assert reviewed.json()["revision"] == workspace["revision"] + 1
    denied = client.post("/api/plan", headers=headers, json={}).json()
    assert denied["id"] != plan["id"]
    assert denied["proposed"]["minimum_balance_cents"] == -40000
    assert denied["state"] == "infeasible"
    assert len(client.get("/api/history", headers=headers).json()) == 2


def test_workspace_chart_reads_persisted_series(api):
    client, store, _, _ = api
    headers, workspace = start(client)
    plan = client.post("/api/plan", headers=headers, json={}).json()
    with store.engine.begin() as connection:
        connection.execute(update(daily_balances).where(daily_balances.c.session_id == workspace["session_id"],
            daily_balances.c.run_id == plan["id"], daily_balances.c.series == "baseline",
            daily_balances.c.event_date == date(2026, 9, 1)).values(balance_cents=199999))
    result = client.get("/api/workspace", headers=headers).json()
    assert result["plan"]["baseline"]["daily"][0]["balance_cents"] == 199999


def test_upload_dedup_versions_originals_and_private_scope(api):
    client, store, _, originals = api
    headers, workspace = start(client, False)
    other_headers, _ = start(client, False)
    response = upload(client, headers)
    assert response.status_code == 201, response.text
    first = response.json()
    assert first["job"] is None and first["document"]["version"] == 1
    assert "not authorized" in first["document"]["error"]
    duplicate = upload(client, headers).json()
    assert duplicate["duplicate"] and duplicate["document"]["id"] == first["document"]["id"]
    same_in_other = upload(client, other_headers).json()
    assert not same_in_other["duplicate"]
    assert same_in_other["document"]["id"] != first["document"]["id"]
    doc_id = first["document"]["id"]
    assert client.get(f"/api/documents/{doc_id}/original", headers=other_headers).status_code == 404
    assert client.delete(f"/api/documents/{doc_id}", headers=other_headers).status_code == 404
    assert client.get(f"/api/documents/{doc_id}/original", headers=headers).text == PAYMENT_TEXT
    changed = PAYMENT_TEXT.replace("$123.45", "$200.00")
    second = upload(client, headers, changed).json()
    assert second["document"]["id"] == doc_id and second["document"]["version"] == 2
    assert client.get(f"/api/documents/{doc_id}/original", headers=headers).text == changed
    assert client.get(f"/api/documents/{doc_id}/original?version=1", headers=headers).text == PAYMENT_TEXT
    keys = store.original_keys(workspace["session_id"], doc_id)
    assert len(keys) == 2 and keys[0] != keys[1]
    assert all(workspace["session_id"] not in key for key in keys)
    assert client.delete(f"/api/documents/{doc_id}", headers=headers).status_code == 200
    assert all(not originals._path(key).exists() for key in keys)
    assert client.get(f"/api/documents/{doc_id}/original?version=1", headers=headers).status_code == 404


@pytest.mark.parametrize("name,content,status", [("evil.exe", b"text", 415), ("evil.pdf", b"not a PDF", 415),
    ("bad.txt", b"binary\x00text", 415), ("bad.txt", b"\xff", 415), ("empty.txt", b"", 422)])
def test_upload_validation(api, name, content, status):
    client, _, _, _ = api
    headers, _ = start(client, False)
    response = client.post("/api/documents", headers=headers, files={"file": (name, content)})
    assert response.status_code == status


def test_live_extraction_http_pipeline_and_human_review(api):
    client, store, providers, originals = api
    providers.settings.nvidia_api_key = "test-key"
    providers.settings.gemini_api_key = "test-key"
    headers, workspace = start(client, False)
    assert intake(client, headers).status_code == 200
    response = upload(client, headers, consent=True).json()
    assert response["job"]["status"] == "queued"
    assert run_once(store, originals, providers)
    result = client.get("/api/workspace", headers=headers).json()
    assert result["jobs"][0]["status"] == "completed"
    assert result["scenario"]["events"] == []
    rule = result["rules"][0]
    assert rule["consequential"] is True
    assert rule["review_status"] == "pending" and rule["approval_status"] == "not_required"
    assert rule["evidence_status"] == "supported"
    reviewed = client.patch(f"/api/rules/{rule['id']}", headers=headers, json={"review_status": "reviewed"})
    assert reviewed.status_code == 200, reviewed.text
    assert reviewed.json()["scenario"]["events"][0]["amount_cents"] == 12345
    assert reviewed.json()["scenario"]["events"][0]["kind"] == "projected"
    assert client.post("/api/plan", headers=headers, json={}).json()["proposed"]["ending_balance_cents"] == 87655
    export = client.get("/api/evidence/export", headers=headers)
    assert "12345" in export.text and PAYMENT_TEXT in export.text
    doc_id = response["document"]["id"]
    assert client.delete(f"/api/documents/{doc_id}", headers=headers).status_code == 200
    current = store.get(workspace["session_id"])
    assert current.scenario.events[0].amount_cents == 12345
    assert current.scenario.events[0].title == "Expense awaiting source review"
    assert current.scenario.events[0].source_rule_ids
    with store.engine.connect() as connection:
        assert connection.execute(select(func.count()).select_from(rule_versions)).scalar() == 0
        assert connection.execute(select(func.count()).select_from(scenario_runs)).scalar() == 0


def test_verifier_failure_requires_explicit_original_confirmation(api):
    client, store, providers, originals = api
    providers.settings.nvidia_api_key = "test-key"
    headers, _ = start(client, False)
    upload(client, headers, consent=True)
    run_once(store, originals, providers)
    workspace = client.get("/api/workspace", headers=headers).json()
    rule = workspace["rules"][0]
    assert rule["evidence_status"] == "disputed" and rule["review_status"] == "unresolved"
    assert "GEMINI_API_KEY" in workspace["documents"][0]["error"]
    url = f"/api/rules/{rule['id']}"
    assert client.patch(url, headers=headers, json={"review_status": "reviewed"}).status_code == 422
    assert client.patch(url, headers=headers, json={"review_status": "reviewed", "evidence_confirmed": True}).status_code == 422
    assert client.patch(url, headers=headers, json={"review_status": "reviewed", "amount_cents": 999,
        "evidence_confirmed": True, "note": "I checked the original"}).status_code == 422
    confirmed = client.patch(url, headers=headers, json={"review_status": "reviewed", "evidence_confirmed": True,
        "note": "Compared amount and date against original synthetic text."})
    assert confirmed.status_code == 200, confirmed.text
    assert confirmed.json()["rules"][0]["evidence_status"] == "supported"


def test_original_hash_tampering_cannot_be_confirmed(api):
    client, store, providers, originals = api
    providers.settings.nvidia_api_key = "test-key"
    headers, workspace = start(client, False)
    response = upload(client, headers, consent=True).json()
    run_once(store, originals, providers)
    rule = store.get(workspace["session_id"]).rules[0]
    key = store.original_key(workspace["session_id"], response["document"]["id"], 1)
    originals._path(key).write_bytes(b"tampered")
    assert client.get(f"/api/documents/{response['document']['id']}/original", headers=headers).status_code == 409
    result = client.patch(f"/api/rules/{rule.id}", headers=headers, json={"review_status": "reviewed",
        "evidence_confirmed": True, "note": "Original checked."})
    assert result.status_code == 409


def test_missing_provider_visible_failure_and_sse_isolation(api):
    client, store, providers, originals = api
    headers, _ = start(client, False)
    other_headers, _ = start(client, False)
    response = upload(client, headers, consent=True).json()
    run_once(store, originals, providers)
    job_id = response["job"]["id"]
    assert client.get(f"/api/jobs/{job_id}", headers=other_headers).status_code == 404
    assert client.get(f"/api/jobs/{job_id}/events", headers=other_headers).status_code == 404
    job = client.get(f"/api/jobs/{job_id}", headers=headers).json()
    assert job["status"] == "failed" and "NVIDIA_API_KEY" in job["error"]
    stream = client.get(f"/api/jobs/{job_id}/events", headers=headers)
    assert 'event: progress' in stream.text and '"status":"failed"' in stream.text
    assert client.get("/api/workspace", headers=headers).json()["documents"][0]["status"] == "failed"


def test_deleted_session_cannot_resurrect_from_worker_or_cache(api):
    client, store, providers, originals = api
    headers, workspace = start(client)
    client.post("/api/plan", headers=headers, json={})
    upload(client, headers, consent=True)
    claimed = store.claim("old-worker")
    assert claimed is not None
    assert client.delete("/api/session", headers=headers).json() == {"deleted": True}
    assert client.get("/api/workspace", headers=headers).status_code == 401
    assert not store.progress(claimed["id"], "old-worker", "completed", 100, "completed")
    assert not run_once(store, originals, providers)
    assert not client.app.state.plan_cache
    with store.engine.connect() as connection:
        for table in (sessions, jobs, financial_events, document_versions, rule_versions, scenario_runs, daily_balances):
            assert connection.execute(select(func.count()).select_from(table)).scalar() == 0
    assert list(originals.root.rglob("v*")) == []


def test_lease_expiry_stale_revision_and_attempt_limit(api):
    client, store, _, _ = api
    _, workspace = start(client, False)
    job = store.enqueue(workspace["session_id"], "document", 1, {"consent": True})
    assert store.claim("first")["id"] == job.id
    assert store.claim("second") is None
    with store.engine.begin() as connection:
        connection.execute(update(jobs).where(jobs.c.id == job.id).values(lease_until=utcnow() - timedelta(seconds=1)))
    assert not store.progress(job.id, "first", "extracting", 20)
    assert store.claim("second")["id"] == job.id
    with pytest.raises(StaleRevision):
        store.mutate(workspace["session_id"], lambda current: None, expected_revision=1,
            job_guard=(job.id, "first"), job_result={})
    store.mutate(workspace["session_id"], lambda current: None, expected_revision=1)
    with pytest.raises(StaleRevision):
        store.mutate(workspace["session_id"], lambda current: None, expected_revision=1)
    with store.engine.begin() as connection:
        connection.execute(update(jobs).where(jobs.c.id == job.id).values(
            lease_until=utcnow() - timedelta(seconds=1), attempts=3))
    assert store.claim("third") is None
    assert store.get_job(workspace["session_id"], job.id).status == "failed"


def test_changed_inputs_while_provider_runs_discards_result(api):
    client, store, providers, originals = api
    headers, workspace = start(client, False)
    providers.settings.nvidia_api_key = "test-key"
    providers.settings.gemini_api_key = "test-key"
    def mutate_during_call(request):
        if request.url.path.endswith("/chat/completions"):
            store.mutate(workspace["session_id"], lambda current: setattr(current.scenario, "opening_balance_cents", 50))
        return transport_handler(request)
    providers.transport = httpx.MockTransport(mutate_during_call)
    response = upload(client, headers, consent=True).json()
    run_once(store, originals, providers)
    current = store.get(workspace["session_id"])
    assert current.rules == [] and current.scenario.opening_balance_cents == 50
    assert store.get_job(workspace["session_id"], response["job"]["id"]).stage == "stale_inputs"


def test_replacement_supersedes_job_and_retry_targets_latest_version(api):
    client, store, _, _ = api
    headers, workspace = start(client, False)
    first = upload(client, headers, consent=True).json()
    replacement_text = PAYMENT_TEXT + " Version two."
    second = upload(client, headers, replacement_text).json()
    assert store.get_job(workspace["session_id"], first["job"]["id"]).stage == "superseded"
    retry = upload(client, headers, replacement_text, consent=True).json()
    assert retry["duplicate"] and retry["job"]["status"] == "queued"
    assert retry["document"]["version"] == 2 == second["document"]["version"]
    job = store.claim("worker")
    assert job["payload"]["document_version"] == 2
    assert job["payload"]["original_key"] == store.original_key(workspace["session_id"], first["document"]["id"], 2)


def test_reset_is_monotonic_and_preserves_other_session(api):
    client, store, _, _ = api
    headers, workspace = start(client)
    other_headers, other = start(client, False)
    client.post("/api/plan", headers=headers, json={})
    reset = client.post("/api/demo/reset", headers=headers).json()
    assert reset["revision"] > workspace["revision"]
    assert reset["plan"] is None and reset["jobs"] == []
    assert client.get("/api/history", headers=headers).json() == []
    assert client.get("/api/workspace", headers=other_headers).json()["session_id"] == other["session_id"]
    with pytest.raises(StaleRevision):
        store.mutate(workspace["session_id"], lambda current: None, expected_revision=workspace["revision"])


def test_conditions_can_be_confirmed_but_not_rewritten(api):
    client, _, _, _ = api
    headers, workspace = start(client)
    rule = next(item for item in workspace["rules"] if item["id"] == "rule-assistance")
    conditions = rule["conditions"]
    conditions[0]["resolved"] = True
    conditions[0]["satisfied"] = True
    response = client.patch("/api/rules/rule-assistance", headers=headers, json={"review_status": "reviewed",
        "approval_status": "pending", "conditions": conditions})
    assert response.status_code == 200, response.text
    assert next(item for item in response.json()["rules"] if item["id"] == "rule-assistance")["conditions"][0]["satisfied"] is True
    conditions[0]["value"] = "invented"
    assert client.patch("/api/rules/rule-assistance", headers=headers,
        json={"review_status": "reviewed", "conditions": conditions}).status_code == 422


def test_intake_actuals_and_strict_integer_money(api):
    client, store, _, _ = api
    headers, workspace = start(client, False)
    event = {"id": "actual", "title": "Recorded payment", "date": "2026-09-01", "amount_cents": 1200,
        "direction": "expense", "kind": "actual"}
    payload = {"opening_balance_cents": 10000, "start_date": "2026-09-01", "events": [event]}
    assert client.post("/api/intake", headers=headers, json=payload).status_code == 200
    with store.engine.connect() as connection:
        assert connection.execute(select(financial_events.c.kind).where(
            financial_events.c.session_id == workspace["session_id"])).scalar() == "actual"
    payload["opening_balance_cents"] = 10.5
    assert client.post("/api/intake", headers=headers, json=payload).status_code == 422
    payload["opening_balance_cents"] = 10000
    payload["events"].append(event)
    assert client.post("/api/intake", headers=headers, json=payload).status_code == 422


def test_audio_and_drafts_require_consent_without_mutating_facts(api):
    client, _, providers, _ = api
    providers.settings.elevenlabs_api_key = "test-key"
    providers.settings.elevenlabs_voice_id = "test-voice"
    headers, workspace = start(client)
    files = {"file": ("intake.wav", b"RIFF-test", "audio/wav")}
    assert client.post("/api/audio/transcribe", headers=headers, files=files).status_code == 403
    response = client.post("/api/audio/transcribe", headers=headers, files=files, data={"consent": "true"})
    assert response.status_code == 200 and response.json()["facts_confirmed"] is False
    assert client.get("/api/workspace", headers=headers).json()["revision"] == workspace["revision"]
    assert client.post("/api/audio/checklist", headers=headers, json={"consent": True}).status_code == 409
    client.post("/api/plan", headers=headers, json={})
    assert client.post("/api/audio/checklist", headers=headers, json={"consent": False}).status_code == 403
    assert client.post("/api/audio/checklist", headers=headers, json={"consent": True}).headers["content-type"] == "audio/mpeg"
    draft = client.post("/api/actions/shift-payment/draft", headers=headers, json={})
    assert draft.status_code == 200 and draft.json()["sent"] is False
    assert client.post("/api/actions/shift-payment/draft", headers=headers,
        json={"use_provider": True, "consent": False}).status_code == 403


def test_provider_retries_are_bounded_and_secrets_are_not_echoed(tmp_path, monkeypatch):
    attempts = []
    monkeypatch.setattr("clausegraph.providers.time.sleep", lambda seconds: None)
    settings = Settings(_env_file=None, provider_retries=2, nvidia_api_key="do-not-print-this")
    def handler(request):
        attempts.append(request)
        return httpx.Response(503, text="do-not-print-this private document")
    providers = Providers(settings, httpx.MockTransport(handler))
    with pytest.raises(ProviderError) as exc:
        providers.request("NVIDIA", "GET", "https://example.invalid")
    assert len(attempts) == 3
    assert "503" in str(exc.value) and "do-not-print-this" not in str(exc.value)
    attempts.clear()
    providers.transport = httpx.MockTransport(lambda request: (attempts.append(request), httpx.Response(401))[1])
    with pytest.raises(ProviderError):
        providers.request("NVIDIA", "GET", "https://example.invalid")
    assert len(attempts) == 1


def test_provider_schema_failure_never_falls_back_to_fixture(api):
    _, _, providers, _ = api
    providers.settings.nvidia_api_key = "test-key"
    providers.transport = httpx.MockTransport(lambda request: httpx.Response(200, json={"choices": [{
        "message": {"content": '{"rules":[{"invented":true}]}'}}]}))
    from clausegraph.demo import load_demo
    scenario, documents, _ = load_demo()
    with pytest.raises(ProviderError, match="invalid extraction schema"):
        providers.extract(documents[0], scenario)


def test_worker_never_calls_provider_without_consent(api):
    client, store, providers, originals = api
    _, workspace = start(client, False)
    job = store.enqueue(workspace["session_id"], "document", 1, {"consent": False})
    providers.transport = httpx.MockTransport(lambda request: pytest.fail("Unexpected external processing"))
    assert run_once(store, originals, providers)
    assert "consent is missing" in store.get_job(workspace["session_id"], job.id).error


def test_short_native_text_proceeds_without_vision(api):
    client, store, providers, originals = api
    providers.settings.nvidia_api_key = "test-key"
    headers, workspace = start(client, False)
    upload(client, headers, text="$123.45 due 2026-09-28", consent=True)
    run_once(store, originals, providers)
    current = store.get(workspace["session_id"])
    assert len(current.rules) == 1
    assert current.jobs[0].status == "completed"


def test_mixed_pdf_preserves_native_pages_and_flags_transcription(api, monkeypatch):
    from pypdf import PdfWriter
    from clausegraph.providers import Verification
    client, store, providers, originals = api
    headers, workspace = start(client, False)
    writer = PdfWriter()
    writer.add_blank_page(100, 100)
    writer.add_blank_page(100, 100)
    stream = io.BytesIO()
    writer.write(stream)
    monkeypatch.setattr("clausegraph.extraction.extract_native", lambda *args: [
        DocumentPage(page=1, text=PAYMENT_TEXT), DocumentPage(page=2, text="")])
    monkeypatch.setattr(providers, "vision", lambda *args: [DocumentPage(page=1, text="Incorrect model rewrite"),
        DocumentPage(page=2, text=PAYMENT_TEXT)])
    def extract(document, scenario):
        assert document.pages[0].text == PAYMENT_TEXT
        result = candidate(document.model_dump(mode="json"))
        result["rules"][0]["evidence"][0]["page"] = 2
        return ExtractionResult.model_validate(result)
    monkeypatch.setattr(providers, "extract", extract)
    monkeypatch.setattr(providers, "verify", lambda document, rules, original: [
        Verification(rule_id=rules[0].id, supported=True, reason="Mock verifier")])
    response = client.post("/api/documents", headers=headers,
        files={"file": ("mixed.pdf", stream.getvalue(), "application/pdf")}, data={"consent": "true"})
    assert response.status_code == 201
    run_once(store, originals, providers)
    current = store.get(workspace["session_id"])
    assert current.documents[0].pages[0].text == PAYMENT_TEXT
    assert current.documents[0].pages[1].text == PAYMENT_TEXT
    assert current.rules[0].evidence_status == "disputed"
    assert "original-page human verification" in current.rules[0].verifier_notes


def test_reviewed_fact_edits_update_projected_candidate_events(api):
    client, store, providers, originals = api
    providers.settings.nvidia_api_key = providers.settings.gemini_api_key = "test-key"
    headers, workspace = start(client, False)
    text = PAYMENT_TEXT + " Correction: payment $200.00 due 2026-09-29."
    upload(client, headers, text=text, consent=True)
    run_once(store, originals, providers)
    rule_id = store.get(workspace["session_id"]).rules[0].id
    response = client.patch(f"/api/rules/{rule_id}", headers=headers, json={"review_status": "reviewed",
        "amount_cents": 20000, "due_date": "2026-09-29", "note": "Confirmed the explicit correction."})
    assert response.status_code == 200, response.text
    assert response.json()["scenario"]["events"][0]["amount_cents"] == 20000
    assert response.json()["scenario"]["events"][0]["date"] == "2026-09-29"
    response = client.patch(f"/api/rules/{rule_id}", headers=headers, json={"review_status": "reviewed"})
    assert response.json()["scenario"]["events"][0]["amount_cents"] == 20000


def test_upload_limit_precedes_multipart_parsing_and_applies_to_chunked(api):
    client, store, providers, originals = api
    settings = providers.settings.model_copy(update={"max_upload_bytes": 1024})
    with TestClient(create_app(settings, store, providers, originals)) as limited:
        headers, _ = start(limited, False)
        oversized = b"x" * (1024 + 65536 + 1)
        assert limited.post("/api/documents", headers=headers, content=oversized).status_code == 413
        assert limited.post("/api/documents", headers=headers,
            content=iter([oversized[:40000], oversized[40000:]])).status_code == 413
        assert limited.post("/api/documents", headers=headers,
            files={"file": ("large.txt", b"x" * 1025)}).status_code == 413


def test_invalid_income_control_returns_validation_error(api):
    client, _, _, _ = api
    headers, _ = start(client, False)
    response = client.post("/api/plan", headers=headers, json={"income_cents": 90000})
    assert response.status_code == 422
