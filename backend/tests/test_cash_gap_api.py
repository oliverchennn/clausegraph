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
    assert cash_gap(client, headers, plan).status_code == 200
    after = client.get("/api/workspace", headers=headers).json()
    assert after["revision"] == before["revision"]
    assert after["scenario"]["opening_balance_cents"] == before["scenario"]["opening_balance_cents"]
    assert after["plan"] == before["plan"]
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
