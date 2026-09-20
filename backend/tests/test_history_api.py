"""History consumption and privacy contracts shared by SQLite and CI PostgreSQL."""
from datetime import date, timedelta
import os
from pathlib import Path
import subprocess
import sys

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, func, select, update

from clausegraph.api import create_app
from clausegraph.config import Settings
from clausegraph.providers import Providers
from clausegraph.schemas import PlanResult, VerificationResult
from clausegraph.storage import (
    MissingSession, Store, daily_balances, scenario_runs, sessions,
    verification_points, verification_runs,
)

HISTORY_TABLES = (scenario_runs, daily_balances, verification_runs, verification_points)


@pytest.fixture(scope="module")
def postgres_url():
    url = os.environ["POSTGRES_TEST_URL"]
    root = Path(__file__).resolve().parents[2]
    subprocess.run([sys.executable, str(root / "scripts/migrate.py")], cwd=root, check=True,
        env={**os.environ, "DATABASE_URL": url, "ENVIRONMENT": "development"})
    return url


@pytest.fixture(params=["sqlite", pytest.param("postgres", marks=pytest.mark.skipif(
    not os.getenv("POSTGRES_TEST_URL"), reason="POSTGRES_TEST_URL not configured"))])
def api(request, tmp_path):
    url = request.getfixturevalue("postgres_url") if request.param == "postgres" else f"sqlite:///{tmp_path / 'history.db'}"
    settings = Settings(_env_file=None, environment="development", database_url=url,
        local_storage_path=tmp_path / "originals", text_provider="nvidia", nvidia_api_key="",
        gemini_api_key="", elevenlabs_api_key="", spaces_endpoint="", spaces_bucket="",
        spaces_access_key_id="", spaces_secret_access_key="")
    store = Store(settings)
    providers = Providers(settings, transport=httpx.MockTransport(
        lambda request: pytest.fail("History validation must not call a provider")))
    owned_sessions = []
    try:
        with TestClient(create_app(settings=settings, store=store, providers=providers)) as client:
            yield client, store, owned_sessions
    finally:
        for session_id in owned_sessions:
            try:
                store.delete_session(session_id)
            except MissingSession:
                pass
        store.engine.dispose()


def start(api):
    client, _, owned_sessions = api
    response = client.post("/api/sessions", json={"demo": True})
    assert response.status_code == 201, response.text
    workspace = response.json()
    owned_sessions.append(workspace["session_id"])
    return {"Authorization": f"Bearer {workspace['session_id']}"}, workspace


def saved_plan(client, headers, **assumptions):
    response = client.post("/api/plan", headers=headers, json=assumptions)
    assert response.status_code == 200, response.text
    return response.json()


def verification(client, headers, plan):
    response = client.post("/api/verify", headers=headers, json={
        "plan_id": plan["id"], "revision": plan["revision"], "uncertainties": []})
    assert response.status_code == 200, response.text
    return response.json()


def counts(store, session_id):
    with store.engine.connect() as connection:
        return [connection.execute(select(func.count()).select_from(table).where(
            table.c.session_id == session_id)).scalar_one() for table in HISTORY_TABLES]


def populate_history(api, headers, session_id, count, *, timestamp=None):
    """Persist copies of one real result to exercise retention without rerunning the solver."""
    client, store, _ = api
    plan = PlanResult.model_validate(saved_plan(client, headers))
    result = VerificationResult.model_validate(verification(client, headers, plan.model_dump(mode="json")))
    for index in range(count):
        recorded = plan.model_copy(deep=True)
        recorded.id = f"plan-{index:02d}"
        recorded.generated_at = timestamp or plan.generated_at + timedelta(seconds=index + 1)
        store.mutate(session_id, lambda current: setattr(current, "plan", recorded), invalidate=False)
        checked = result.model_copy(deep=True)
        checked.id = f"verification-{index:02d}"
        checked.plan_id = checked.assumptions.plan_id = recorded.id
        checked.generated_at = timestamp or result.generated_at + timedelta(seconds=index + 1)
        store.save_verification(session_id, checked)
    return plan, result


def test_history_reads_require_authentication_and_do_not_mutate_or_compute(api, monkeypatch):
    import clausegraph.engine as engine
    import clausegraph.verification as verifier

    client, store, _ = api
    headers, workspace = start(api)
    other_headers, _ = start(api)
    plan = saved_plan(client, headers)
    checked = verification(client, headers, plan)
    sid = workspace["session_id"]
    with store.engine.connect() as connection:
        before = connection.execute(select(sessions.c.snapshot, sessions.c.revision).where(sessions.c.id == sid)).one()
    before_counts = counts(store, sid)
    monkeypatch.setattr(engine, "optimize", lambda *a, **kw: pytest.fail("History read ran the optimizer"))
    monkeypatch.setattr(verifier, "verify_plan", lambda *a, **kw: pytest.fail("History read ran verification"))
    for path, expected in (("/api/history", [plan]), ("/api/verifications", [checked])):
        assert client.get(path).status_code == 401
        assert client.get(path, headers={"Authorization": "Bearer missing-session"}).status_code == 401
        assert client.get(path, headers=other_headers).json() == []
        for _ in range(2):
            response = client.get(path, headers=headers)
            assert response.status_code == 200, response.text
            assert response.headers["cache-control"] == "no-store"
            assert response.json() == expected
    with store.engine.connect() as connection:
        after = connection.execute(select(sessions.c.snapshot, sessions.c.revision).where(sessions.c.id == sid)).one()
    assert after == before
    assert counts(store, sid) == before_counts


def test_history_keeps_plan_identity_assumptions_and_old_revisions(api):
    client, _, _ = api
    headers, workspace = start(api)
    first = saved_plan(client, headers)
    first_check = verification(client, headers, first)
    assumed = saved_plan(client, headers, opening_balance_cents=240000)
    assumed_check = verification(client, headers, assumed)
    assert first["id"] != assumed["id"] and first["revision"] == assumed["revision"]
    assert assumed_check["nominal_assumptions"]["opening_balance_cents"] == 240000

    preview = client.post("/api/plan/preview", headers=headers, json={"opening_balance_cents": 250000})
    assert preview.status_code == 200, preview.text
    # A cached result can become active again without becoming the newest history entry.
    assert saved_plan(client, headers)["id"] == first["id"]
    assert [item["id"] for item in client.get("/api/history", headers=headers).json()] == [assumed["id"], first["id"]]
    assert client.get("/api/workspace", headers=headers).json()["plan"]["id"] == first["id"]
    changed = client.patch("/api/rules/rule-shift", headers=headers,
        json={"review_status": "reviewed", "approval_status": "denied"})
    assert changed.status_code == 200, changed.text
    current = saved_plan(client, headers)
    assert current["revision"] == workspace["revision"] + 1
    assert current["state"] == "infeasible"
    assert {item["id"]: item for item in client.get("/api/history", headers=headers).json()} == {
        item["id"]: item for item in (first, assumed, current)}
    assert client.get("/api/verifications", headers=headers).json() == [assumed_check, first_check]
    stale = client.post("/api/verify", headers=headers,
        json={"plan_id": first["id"], "revision": first["revision"]})
    assert stale.status_code == 409
    assert client.get("/api/workspace", headers=headers).json()["plan"] == current


def test_history_limit_has_stable_ties_and_durable_chart_readback(api, monkeypatch):
    import clausegraph.storage as storage

    client, store, _ = api
    headers, workspace = start(api)
    timestamp = storage.utcnow() + timedelta(days=1)
    monkeypatch.setattr(storage, "utcnow", lambda: timestamp)
    plan, _ = populate_history(api, headers, workspace["session_id"], 33, timestamp=timestamp)
    with store.engine.begin() as connection:
        connection.execute(update(daily_balances).where(
            daily_balances.c.session_id == workspace["session_id"], daily_balances.c.run_id == "plan-31",
            daily_balances.c.series == "baseline", daily_balances.c.event_date == plan.baseline.daily[0].date)
            .values(balance_cents=199999))
    restored = Store(store.settings)
    try:
        with TestClient(create_app(settings=store.settings, store=restored)) as reopened:
            plans = reopened.get("/api/history", headers=headers).json()
            checked = reopened.get("/api/verifications", headers=headers).json()
            assert [item["id"] for item in plans] == [f"plan-{index:02d}" for index in range(32, 2, -1)]
            assert [item["id"] for item in checked] == [f"verification-{index:02d}" for index in range(32, 2, -1)]
            assert plans[1]["baseline"]["daily"][0]["balance_cents"] == 199999
            assert plans[1]["baseline"]["daily"][0]["event_ids"] == plan.baseline.daily[0].event_ids
            assert counts(restored, workspace["session_id"])[::2] == [34, 34]
    finally:
        restored.engine.dispose()


@pytest.mark.parametrize("path,table,run_key,series", [
    ("/api/history", daily_balances, "plan", "baseline"),
    ("/api/verifications", verification_points, "verification", "worst_case"),
])
def test_incomplete_historical_chart_fails_closed_without_payload_fallback(api, path, table, run_key, series):
    client, store, _ = api
    headers, workspace = start(api)
    plan = saved_plan(client, headers)
    checked = verification(client, headers, plan)
    active = saved_plan(client, headers, opening_balance_cents=210000)
    run = plan if run_key == "plan" else checked
    with store.engine.begin() as connection:
        connection.execute(delete(table).where(table.c.session_id == workspace["session_id"],
            table.c.run_id == run["id"], table.c.series == series,
            table.c.event_date == date.fromisoformat(plan["baseline"]["daily"][0]["date"])))
    with TestClient(client.app, raise_server_exceptions=False) as failure_client:
        response = failure_client.get(path, headers=headers)
        assert response.status_code == 500
        assert response.text == "Internal Server Error"
    assert client.get("/api/workspace", headers=headers).json()["plan"] == active


@pytest.mark.parametrize("operation", ["source", "reset", "session"])
def test_deletion_purges_all_history_beyond_display_limit_and_preserves_other_session(api, operation):
    client, store, _ = api
    headers, workspace = start(api)
    other_headers, other = start(api)
    populate_history(api, headers, workspace["session_id"], 31)
    # Deliberately reuse run IDs in another session to check composite-key isolation.
    populate_history(api, other_headers, other["session_id"], 1)
    paths = ("/api/history", "/api/verifications")
    other_before = [client.get(path, headers=other_headers).json() for path in paths]
    other_counts = counts(store, other["session_id"])
    assert counts(store, workspace["session_id"])[::2] == [32, 32]
    for path in paths:
        assert len(client.get(path, headers=headers).json()) == 30
    if operation == "source":
        removed = client.delete("/api/documents/doc-3", headers=headers)
    elif operation == "reset":
        removed = client.post("/api/demo/reset", headers=headers)
    else:
        removed = client.delete("/api/session", headers=headers)
    assert removed.status_code == 200, removed.text
    assert counts(store, workspace["session_id"]) == [0, 0, 0, 0]
    for index, path in enumerate(paths):
        response = client.get(path, headers=headers)
        assert response.status_code == (401 if operation == "session" else 200)
        if operation != "session":
            assert response.json() == []
        assert client.get(path, headers=other_headers).json() == other_before[index]
    assert counts(store, other["session_id"]) == other_counts
