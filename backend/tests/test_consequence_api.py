"""Current-source, nonmutating consequence previews on SQLite and CI PostgreSQL."""
# ruff: noqa: F811 -- shared pytest fixtures are injected as parameters
import pytest

from clausegraph import engine
from test_history_api import api, counts, postgres_url, saved_plan, start  # noqa: F401


CANCELLATION = {"force_action_ids": ["cancel-phone"],
    "exclude_action_ids": ["shift-payment", "claim-assistance"]}


def preview(client, headers, body):
    response = client.post("/api/plan/preview", headers=headers, json=body)
    assert response.status_code == 200, response.text
    return response.json()


def test_preview_binds_source_and_preserves_ledger_history_and_cache(api):
    client, store, _ = api
    headers, workspace = start(api)
    sid = workspace["session_id"]
    source = saved_plan(client, headers)
    snapshot, rows = store.get(sid).model_dump_json(), counts(store, sid)
    result = preview(client, headers, CANCELLATION)
    assert result["preview_source_plan_id"] == source["id"]
    assert result["revision"] == source["revision"]
    assert result["state"] == "infeasible"  # Cash failure is distinct from blocked permission.
    assert result["proposed"]["minimum_balance_cents"] == -82000
    assert result["proposed"]["ending_balance_cents"] == 8000
    remove, accelerate = result["decision_traces"][0]["changes"]
    assert remove["operation"] == "remove" and remove["before"]["amount_cents"] == 6000
    assert accelerate["operation"] == "accelerate"
    assert accelerate["before"]["obligation_id"] == accelerate["after"]["obligation_id"] == "device"
    assert accelerate["before"]["amount_cents"] == accelerate["after"]["amount_cents"] == 48000
    assert not result["proposed"]["beyond_horizon"]
    assert source["proposed"]["beyond_horizon"][0]["obligation_id"] == "device"
    assert store.get(sid).model_dump_json() == snapshot and counts(store, sid) == rows
    assert preview(client, headers, CANCELLATION) == result
    saved = saved_plan(client, headers, **CANCELLATION)
    assert saved["id"] == result["id"] and saved["preview_source_plan_id"] is None
    # A cache hit still binds to today's saved plan, not the source of the first preview.
    assert preview(client, headers, CANCELLATION)["preview_source_plan_id"] == saved["id"]


def test_preview_without_saved_plan_and_private_scope(api):
    client, store, _ = api
    headers, workspace = start(api)
    result = preview(client, headers, {})
    assert result["preview_source_plan_id"] is None
    assert store.get(workspace["session_id"]).plan is None
    assert client.get("/api/history", headers=headers).json() == []
    assert client.post("/api/plan/preview", json={}).status_code == 401
    other, _ = start(api)
    assert preview(client, other, {})["id"] != result["id"]


@pytest.mark.parametrize("race", ["revision", "active_plan", "remove_plan", "source_status", "source_version", "delete"])
def test_preview_rejects_changes_during_computation(api, monkeypatch, race):
    client, store, _ = api
    headers, workspace = start(api)
    sid = workspace["session_id"]
    saved_plan(client, headers)
    original = engine.optimize

    def changing(*args, **kwargs):
        result = original(*args, **kwargs)
        if race == "delete":
            store.delete_session(sid)
        elif race == "revision":
            store.mutate(sid, lambda current: None)
        elif race == "active_plan":
            store.mutate(sid, lambda current: setattr(current.plan, "id", "new-plan"), invalidate=False)
        elif race == "remove_plan":
            store.mutate(sid, lambda current: setattr(current, "plan", None), invalidate=False)
        elif race == "source_status":
            store.mutate(sid, lambda current: setattr(current.documents[0], "status", "failed"), invalidate=False)
        else:
            store.mutate(sid, lambda current: setattr(current.documents[0], "version", 2), invalidate=False)
        return result

    monkeypatch.setattr(engine, "optimize", changing)
    response = client.post("/api/plan/preview", headers=headers, json=CANCELLATION)
    assert response.status_code == (401 if race == "delete" else 409), response.text
    if race == "delete":
        assert not any(key[0] == sid for key in client.app.state.plan_cache)


def test_status_only_changes_cannot_reuse_obsolete_cached_readiness(api):
    client, store, _ = api
    headers, workspace = start(api)
    sid = workspace["session_id"]
    source = saved_plan(client, headers)
    assert preview(client, headers, {})["state"] == "confirmed"
    store.mutate(sid, lambda current: setattr(current.documents[0], "status", "failed"), invalidate=False)
    unresolved = preview(client, headers, {})
    assert unresolved["state"] == "unresolved"
    assert unresolved["preview_source_plan_id"] == source["id"]
    assert any("source processing is incomplete" in warning for warning in unresolved["warnings"])
    store.mutate(sid, lambda current: setattr(current.documents[0], "status", "ready"), invalidate=False)
    assert preview(client, headers, {})["state"] == "confirmed"
    assert [item.id for item in store.history(sid)] == [source["id"]]


def test_blocked_action_has_no_authorized_trace_or_fabricated_benefit(api):
    client, store, _ = api
    headers, workspace = start(api)
    source = saved_plan(client, headers)
    result = preview(client, headers, {"force_action_ids": ["claim-assistance"],
        "exclude_action_ids": ["shift-payment", "cancel-phone"]})
    assert result["preview_source_plan_id"] == source["id"]
    assert not result["actions"] and not result["decision_traces"]
    assert "approval is pending" in result["excluded_actions"]["claim-assistance"]
    assert store.get(workspace["session_id"]).plan.id == source["id"]
