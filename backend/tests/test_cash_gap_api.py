"""Private, nonmutating cash-gap endpoint: session scope, revision races, no persistence."""
import pytest
from fastapi.testclient import TestClient

from clausegraph.api import create_app
from clausegraph.config import Settings
from clausegraph.storage import Store


@pytest.fixture
def api(tmp_path):
    settings = Settings(_env_file=None, database_url=f"sqlite:///{tmp_path / 'cash-gap.db'}",
        local_storage_path=tmp_path / "originals", nvidia_api_key="", gemini_api_key="",
        elevenlabs_api_key="", spaces_endpoint="", spaces_bucket="", spaces_access_key_id="",
        spaces_secret_access_key="")
    store = Store(settings)
    with TestClient(create_app(settings=settings, store=store)) as client:
        yield client, store
    store.engine.dispose()


def start(client):
    response = client.post("/api/sessions", json={"demo": True})
    assert response.status_code == 201, response.text
    workspace = response.json()
    return {"Authorization": f"Bearer {workspace['session_id']}"}, workspace


def current_plan(client, headers, **assumptions):
    response = client.post("/api/plan", headers=headers, json=assumptions)
    assert response.status_code == 200, response.text
    return response.json()


def payday_dimension():
    return {"id": "payday", "kind": "income_date", "event_id": "paycheck",
            "earliest": "2026-09-21", "latest": "2026-09-28", "basis": "user_assumption",
            "rationale": "User-declared delay window."}


def cash_gap(client, headers, plan, **overrides):
    return client.post("/api/cash-gap", headers=headers, json={
        "plan_id": plan["id"], "revision": plan["revision"],
        "uncertainties": [payday_dimension()], **overrides})


def test_diagnostic_returns_the_proven_buffer(api):
    client, _ = api
    headers, _ = start(client)
    plan = current_plan(client, headers)
    response = cash_gap(client, headers, plan)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["mode"] == "cash_gap_diagnostic"
    assert body["status"] == "PROVEN_MINIMUM"
    assert body["additional_opening_cash_cents"] == 40000
    assert body["is_funding"] is False
    assert body["limiting_date"] == "2026-09-26"


def test_diagnostic_persists_nothing_and_leaves_the_workspace_alone(api):
    client, _ = api
    headers, workspace = start(client)
    plan = current_plan(client, headers)
    before = client.get("/api/workspace", headers=headers).json()
    history = client.get("/api/history", headers=headers).json()
    assert cash_gap(client, headers, plan).status_code == 200
    after = client.get("/api/workspace", headers=headers).json()
    assert after == before
    assert client.get("/api/history", headers=headers).json() == history
    # The internal verifications it runs are diagnostics, not saved verification history.
    assert client.get("/api/verifications", headers=headers).json() == []


def test_diagnostic_requires_a_session(api):
    client, _ = api
    headers, _ = start(client)
    plan = current_plan(client, headers)
    assert client.post("/api/cash-gap", json={"plan_id": plan["id"], "revision": plan["revision"],
                                              "uncertainties": []}).status_code == 401


def test_another_session_cannot_diagnose_this_plan(api):
    client, _ = api
    headers, _ = start(client)
    plan = current_plan(client, headers)
    other_headers, _ = start(client)
    response = cash_gap(client, other_headers, plan)
    assert response.status_code == 409
    assert "current saved plan" in response.json()["detail"]


def test_stale_revision_is_rejected(api):
    client, _ = api
    headers, _ = start(client)
    plan = current_plan(client, headers)
    stale = dict(plan, revision=plan["revision"] + 1)
    assert cash_gap(client, headers, stale).status_code in (409, 422)


def test_a_workspace_change_invalidates_the_old_plan_reference(api):
    client, _ = api
    headers, workspace = start(client)
    plan = current_plan(client, headers)
    intake = client.post("/api/intake", headers=headers, json={
        "opening_balance_cents": workspace["scenario"]["opening_balance_cents"],
        "start_date": workspace["scenario"]["start_date"],
        "horizon_days": workspace["scenario"]["horizon_days"],
        "events": workspace["scenario"]["events"],
        "essential_service_ids": workspace["scenario"]["essential_service_ids"]})
    assert intake.status_code == 200, intake.text
    assert cash_gap(client, headers, plan).status_code == 409


@pytest.mark.parametrize("phase", ["uploaded", "extracting", "failed", "needs_review", "old_version"])
def test_incomplete_sources_block_diagnostic_before_computation(api, monkeypatch, phase):
    import clausegraph.cash_gap as diagnostic

    client, store = api
    headers, workspace = start(client)
    other_headers, _ = start(client)
    other_plan = current_plan(client, other_headers)

    def incomplete(current):
        document = current.documents[0]
        document.status = "needs_review" if phase == "old_version" else phase
        if phase == "needs_review":
            # An empty extraction has no current rule representation.
            current.rules = [rule for rule in current.rules if not any(
                source.document_id == document.id for source in rule.evidence)]
        elif phase == "old_version":
            document.version += 1

    store.mutate(workspace["session_id"], incomplete)
    plan = current_plan(client, headers)
    assert plan["state"] == "unresolved"
    before = store.get(workspace["session_id"]).model_dump(mode="json")
    history = client.get("/api/history", headers=headers).json()
    original = diagnostic.diagnose_cash_gap
    calls = []

    def record_call(*args):
        calls.append(args[2].id)
        return original(*args)

    monkeypatch.setattr(diagnostic, "diagnose_cash_gap", record_call)
    response = cash_gap(client, headers, plan)
    assert response.status_code == 409, response.json().get("status", response.json())
    assert "source processing is incomplete" in response.json()["detail"]
    assert calls == []
    assert store.get(workspace["session_id"]).model_dump(mode="json") == before
    assert client.get("/api/history", headers=headers).json() == history
    assert client.get("/api/verifications", headers=headers).json() == []
    # This session's source problem cannot block another private session.
    assert cash_gap(client, other_headers, other_plan).json()["status"] == "PROVEN_MINIMUM"


def test_unprocessed_upload_cannot_claim_zero_gap_even_for_legacy_confirmed_plan(api):
    client, store = api
    created = client.post("/api/sessions", json={"demo": False})
    assert created.status_code == 201
    session_id = created.json()["session_id"]
    headers = {"Authorization": f"Bearer {session_id}"}
    upload = client.post("/api/documents", headers=headers,
        files={"file": ("synthetic-bill.txt", b"SYNTHETIC. Pay $123.45 on 2026-09-28.", "text/plain")},
        data={"consent": "false"})
    assert upload.status_code == 201, upload.text
    plan = current_plan(client, headers)
    assert plan["state"] == "unresolved"

    def legacy_confirmed(current):
        current.plan.state = "confirmed"

    store.mutate(session_id, legacy_confirmed, invalidate=False)
    before = store.get(session_id).model_dump(mode="json")
    response = cash_gap(client, headers, plan, uncertainties=[])
    assert response.status_code == 409, response.json().get("status", response.json())
    assert "source processing is incomplete" in response.json()["detail"]
    assert store.get(session_id).model_dump(mode="json") == before
    assert client.get("/api/verifications", headers=headers).json() == []


def test_represented_source_review_remains_an_engine_gate(api):
    client, store = api
    headers, workspace = start(client)

    def awaiting_review(current):
        rule = next(rule for rule in current.rules if rule.id == "rule-loan")
        rule.review_status = "pending"
        document = next(document for document in current.documents if document.id == rule.evidence[0].document_id)
        document.status = "needs_review"

    store.mutate(workspace["session_id"], awaiting_review)
    plan = current_plan(client, headers)
    response = cash_gap(client, headers, plan)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["baseline"]["status"] != "SAFE"
    assert body["additional_opening_cash_cents"] is None
    assert body["minimality_proven"] is False


@pytest.mark.parametrize("race", ["revision", "active_plan", "missing_plan", "source_delete", "reset", "delete"])
def test_changed_workspace_withholds_in_flight_diagnostic(api, monkeypatch, race):
    import clausegraph.cash_gap as diagnostic

    client, store = api
    headers, workspace = start(client)
    plan = current_plan(client, headers)
    original = diagnostic.diagnose_cash_gap
    after_change = {}

    def changed_during_run(*args):
        result = original(*args)
        if race == "delete":
            changed = client.delete("/api/session", headers=headers)
            assert changed.status_code == 200, changed.text
        else:
            if race == "revision":
                changed = client.patch("/api/rules/rule-shift", headers=headers,
                    json={"review_status": "reviewed", "approval_status": "denied"})
                assert changed.status_code == 200, changed.text
            elif race == "active_plan":
                replacement = current_plan(client, headers, opening_balance_cents=210000)
                assert replacement["id"] != plan["id"]
                assert replacement["revision"] == plan["revision"]
            elif race == "missing_plan":
                def remove_plan(current):
                    current.plan = None
                store.mutate(workspace["session_id"], remove_plan, invalidate=False)
            elif race == "source_delete":
                changed = client.delete(f"/api/documents/{workspace['documents'][0]['id']}", headers=headers)
                assert changed.status_code == 200, changed.text
            else:
                changed = client.post("/api/demo/reset", headers=headers)
                assert changed.status_code == 200, changed.text
            after_change["workspace"] = store.get(workspace["session_id"]).model_dump(mode="json")
            after_change["history"] = client.get("/api/history", headers=headers).json()
        return result

    monkeypatch.setattr(diagnostic, "diagnose_cash_gap", changed_during_run)
    response = cash_gap(client, headers, plan)
    assert response.status_code == (401 if race == "delete" else 409), response.json().get("status")
    assert "baseline" not in response.json()
    if race == "delete":
        assert client.get("/api/workspace", headers=headers).status_code == 401
    else:
        assert store.get(workspace["session_id"]).model_dump(mode="json") == after_change["workspace"]
        assert client.get("/api/history", headers=headers).json() == after_change["history"]
        assert client.get("/api/verifications", headers=headers).json() == []


def test_other_session_changes_do_not_discard_current_diagnostic(api, monkeypatch):
    import clausegraph.cash_gap as diagnostic

    client, store = api
    headers, workspace = start(client)
    other_headers, _ = start(client)
    plan = current_plan(client, headers)
    before = store.get(workspace["session_id"]).model_dump(mode="json")
    original = diagnostic.diagnose_cash_gap

    def other_session_changes(*args):
        result = original(*args)
        assert client.post("/api/demo/reset", headers=other_headers).status_code == 200
        return result

    monkeypatch.setattr(diagnostic, "diagnose_cash_gap", other_session_changes)
    response = cash_gap(client, headers, plan)
    assert response.status_code == 200, response.text
    assert response.json()["additional_opening_cash_cents"] == 40000
    assert store.get(workspace["session_id"]).model_dump(mode="json") == before
