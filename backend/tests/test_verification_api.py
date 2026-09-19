"""Private fixed-plan verification, revision races and durable history privacy."""
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, func, select, update

from clausegraph.api import create_app
from clausegraph.config import Settings
from clausegraph.schemas import VerificationResult
from clausegraph.storage import Store, sessions, verification_points, verification_runs


@pytest.fixture
def api(tmp_path):
    settings = Settings(_env_file=None, database_url=f"sqlite:///{tmp_path / 'verification.db'}",
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
    headers = {"Authorization": f"Bearer {workspace['session_id']}"}
    return headers, workspace


def current_plan(client, headers, **assumptions):
    response = client.post("/api/plan", headers=headers, json=assumptions)
    assert response.status_code == 200, response.text
    return response.json()


def verify(client, headers, plan, **overrides):
    return client.post("/api/verify", headers=headers,
        json={"plan_id": plan["id"], "revision": plan["revision"], "uncertainties": [], **overrides})


def row_count(store, table, session_id):
    with store.engine.connect() as connection:
        return connection.execute(select(func.count()).select_from(table).where(
            table.c.session_id == session_id)).scalar_one()


def test_verify_saved_plan_is_scoped_and_does_not_optimize_or_change_workspace(api, monkeypatch):
    import clausegraph.engine as engine

    client, store = api
    headers, workspace = start(client)
    plan = current_plan(client, headers)
    before = store.get(workspace["session_id"]).model_dump(mode="json")
    with monkeypatch.context() as patch:
        patch.setattr(engine, "optimize", lambda *args, **kwargs: pytest.fail("Verification must not optimize"))
        response = verify(client, headers, plan)
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["status"] == "SAFE"
    assert result["mode"] == "verify_fixed_plan"
    assert result["fixed_actions"] == plan["actions"]
    assert result["plan_id"] == plan["id"] and result["revision"] == plan["revision"]
    assert store.get(workspace["session_id"]).model_dump(mode="json") == before
    assert client.get("/api/history", headers=headers).json() == [plan]
    assert client.get("/api/verifications", headers=headers).json() == [result]
    other_headers, other = start(client)
    other_plan = current_plan(client, other_headers)
    assert client.get("/api/verifications", headers=other_headers).json() == []
    assert verify(client, other_headers, plan).status_code == 409
    assert client.get("/api/verifications").status_code == 401
    assert verify(client, {}, other_plan).status_code == 401
    assert row_count(store, verification_runs, other["session_id"]) == 0


def test_verification_rejects_absent_foreign_and_stale_plan_before_engine(api, monkeypatch):
    import clausegraph.verification as verification

    client, store = api
    headers, workspace = start(client)
    assert verify(client, headers, {"id": "absent", "revision": workspace["revision"]}).status_code == 409
    old = current_plan(client, headers)
    new = current_plan(client, headers, opening_balance_cents=210000)
    assert old["id"] != new["id"]
    monkeypatch.setattr(verification, "verify_plan", lambda *args, **kwargs: pytest.fail("Stale input reached verifier"))
    assert verify(client, headers, old).status_code == 409
    response = client.patch("/api/rules/rule-shift", headers=headers,
        json={"review_status": "reviewed", "approval_status": "denied"})
    assert response.status_code == 200, response.text
    assert verify(client, headers, new).status_code == 409
    assert row_count(store, verification_runs, workspace["session_id"]) == 0


@pytest.mark.parametrize("race", ["revision", "active_plan", "delete"])
def test_result_is_not_saved_if_workspace_changes_during_verification(api, monkeypatch, race):
    import clausegraph.verification as verification

    client, store = api
    headers, workspace = start(client)
    plan = current_plan(client, headers)
    original = verification.verify_plan

    def changed_during_run(*args):
        result = original(*args)
        if race == "delete":
            store.delete_session(workspace["session_id"])
        elif race == "revision":
            store.mutate(workspace["session_id"], lambda current: None)
        else:
            # A new nominal plan need not change the workspace input revision.
            def replace(current):
                current.plan.id = "different-plan-at-same-revision"
            store.mutate(workspace["session_id"], replace, invalidate=False)
        return result

    monkeypatch.setattr(verification, "verify_plan", changed_during_run)
    assert verify(client, headers, plan).status_code == (401 if race == "delete" else 409)
    assert row_count(store, verification_runs, workspace["session_id"]) == 0
    assert row_count(store, verification_points, workspace["session_id"]) == 0


def test_verification_history_is_newest_thirty_and_restores_persisted_points(api):
    client, store = api
    headers, workspace = start(client)
    plan = current_plan(client, headers)
    response = verify(client, headers, plan)
    assert response.status_code == 200, response.text
    result = VerificationResult.model_validate(response.json())
    for index in range(31):
        recorded = result.model_copy(deep=True)
        recorded.id = f"history-{index:02d}"
        recorded.generated_at += timedelta(seconds=index + 1)
        store.save_verification(workspace["session_id"], recorded)
    with store.engine.begin() as connection:
        connection.execute(update(verification_points).where(
            verification_points.c.session_id == workspace["session_id"],
            verification_points.c.run_id == "history-30", verification_points.c.event_date == result.horizon_start)
            .values(balance_cents=123456))
    restored_store = Store(store.settings)
    try:
        history = restored_store.verifications(workspace["session_id"])
        assert len(history) == 30
        assert history[0].id == "history-30" and history[-1].id == "history-01"
        assert history[0].worst_case.daily[0].balance_cents == 123456
        assert history[0].worst_case.daily[0].event_ids == result.worst_case.daily[0].event_ids
    finally:
        restored_store.engine.dispose()
    assert len(client.get("/api/verifications", headers=headers).json()) == 30
    with store.engine.begin() as connection:
        connection.execute(delete(verification_points).where(
            verification_points.c.session_id == workspace["session_id"],
            verification_points.c.run_id == "history-30", verification_points.c.event_date == result.horizon_start))
    with pytest.raises(RuntimeError, match="verification chart series is incomplete"):
        store.verifications(workspace["session_id"])


@pytest.mark.parametrize("operation", ["source", "reset", "session"])
def test_deletion_and_reset_purge_verification_narratives_and_points_privately(api, operation):
    client, store = api
    headers, workspace = start(client)
    plan = current_plan(client, headers)
    response = verify(client, headers, plan)
    assert response.status_code == 200, response.text
    other_headers, other = start(client)
    other_plan = current_plan(client, other_headers)
    assert verify(client, other_headers, other_plan).status_code == 200
    assert row_count(store, verification_points, workspace["session_id"]) > 0
    if operation == "source":
        deleted = client.delete("/api/documents/doc-3", headers=headers)
    elif operation == "reset":
        deleted = client.post("/api/demo/reset", headers=headers)
    else:
        deleted = client.delete("/api/session", headers=headers)
    assert deleted.status_code == 200, deleted.text
    assert row_count(store, verification_runs, workspace["session_id"]) == 0
    assert row_count(store, verification_points, workspace["session_id"]) == 0
    assert row_count(store, verification_runs, other["session_id"]) == 1
    assert row_count(store, verification_points, other["session_id"]) > 0
    history = client.get("/api/verifications", headers=headers)
    assert history.status_code == (401 if operation == "session" else 200)
    if operation != "session":
        assert history.json() == []


def test_bad_uncertainty_cannot_persist_or_mutate_current_plan(api):
    client, store = api
    headers, workspace = start(client)
    plan = current_plan(client, headers)
    response = verify(client, headers, plan, uncertainties=[{
        "id": "bad-income", "kind": "income_date", "event_id": "unknown-event",
        "earliest": "2026-09-21", "latest": "2026-09-28", "rationale": "User declared test range",
    }])
    assert response.status_code == 422, response.text
    assert row_count(store, verification_runs, workspace["session_id"]) == 0
    assert client.get("/api/workspace", headers=headers).json()["plan"] == plan


def test_unknown_result_remains_unknown_in_persisted_history(api):
    client, _ = api
    headers, workspace = start(client)
    plan = current_plan(client, headers)
    income = next(event for event in workspace["scenario"]["events"] if event["direction"] == "income")
    response = verify(client, headers, plan, max_cases=1, uncertainties=[{
        "id": "bounded-payday", "kind": "income_date", "event_id": income["id"],
        "earliest": "2026-09-21", "latest": "2026-09-28", "rationale": "User declared payday range",
    }])
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["status"] == "UNKNOWN" and result["solver_status"] == "CASE_LIMIT"
    assert not result["coverage_complete"]
    assert client.get("/api/verifications", headers=headers).json()[0]["status"] == "UNKNOWN"


def test_unsafe_counterexample_and_event_trace_survive_history_reload(api):
    client, _ = api
    headers, workspace = start(client)
    plan = current_plan(client, headers)
    income = next(event for event in workspace["scenario"]["events"] if event["direction"] == "income")
    response = verify(client, headers, plan, uncertainties=[{
        "id": "bounded-payday", "kind": "income_date", "event_id": income["id"],
        "earliest": "2026-09-21", "latest": "2026-09-28", "rationale": "User declared payday range",
    }])
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["status"] == "UNSAFE" and result["coverage_complete"]
    assert result["worst_case"]["minimum_balance_cents"] == -40000
    assert result["counterexample"]["earliest_failing_date"] == "2026-09-26"
    assert result["counterexample"]["events"]
    assert client.get("/api/verifications", headers=headers).json() == [result]
    assert client.get("/api/workspace", headers=headers).json()["plan"] == plan


def test_verification_save_leaves_raw_session_snapshot_unchanged(api):
    client, store = api
    headers, workspace = start(client)
    plan = current_plan(client, headers)
    with store.engine.connect() as connection:
        before = connection.execute(select(sessions.c.snapshot, sessions.c.revision).where(
            sessions.c.id == workspace["session_id"])).one()
    assert verify(client, headers, plan).status_code == 200
    with store.engine.connect() as connection:
        after = connection.execute(select(sessions.c.snapshot, sessions.c.revision).where(
            sessions.c.id == workspace["session_id"])).one()
    assert after == before
