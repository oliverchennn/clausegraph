"""Nonmutating previews and atomic adoption on SQLite and CI PostgreSQL."""
# ruff: noqa: F811 -- imported pytest fixture names are injected as parameters
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest

from clausegraph import synthesis
from test_history_api import api, counts, postgres_url  # noqa: F401 -- shared database fixtures


def start(api, variant="resilient"):
    client, store, owned = api
    response = client.post("/api/sessions", json={"demo": True, "demo_variant": variant})
    assert response.status_code == 201, response.text
    workspace = response.json()
    owned.append(workspace["session_id"])
    headers = {"Authorization": f"Bearer {workspace['session_id']}"}
    plan = client.post("/api/plan", headers=headers, json={}).json()
    body = {"plan_id": plan["id"], "revision": workspace["revision"], "uncertainties": [{
        "id": "payday", "kind": "income_date", "event_id": "resilient-paycheck", "earliest": "2026-09-03",
        "latest": "2026-09-05", "rationale": "Separate synthetic assumption."}]}
    return headers, workspace, plan, body


def preview(client, headers, body):
    response = client.post("/api/synthesis", headers=headers, json=body)
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["status"] == "FOUND"
    return result


def adoption(result):
    return {"synthesis_request": result["assumptions"], "candidate_fingerprint": result["candidate_fingerprint"],
        "selected_actions": [{"action_id": a["action_id"], "execution_date": a["execution_date"]} for a in result["candidate"]["actions"]]}


def test_preview_nonmutation_then_explicit_atomic_adoption_and_replay(api, monkeypatch):
    client, store, _ = api
    headers, workspace, source, body = start(api)
    sid = workspace["session_id"]
    before, before_counts = store.get(sid).model_dump_json(), counts(store, sid)
    for document in workspace["documents"]:
        response = client.get(f"/api/documents/{document['id']}/original", headers=headers)
        assert response.status_code == 200 and "SYNTHETIC" in response.text
    import clausegraph.engine as engine
    monkeypatch.setattr(engine, "optimize", lambda *a, **k: pytest.fail("Synthesis/adoption may not optimize"))
    result = preview(client, headers, body)
    assert store.get(sid).model_dump_json() == before and counts(store, sid) == before_counts
    response = client.post("/api/synthesis/adopt", headers=headers, json=adoption(result))
    assert response.status_code == 200, response.text
    saved = response.json()
    assert saved["plan"]["id"] not in (source["id"], result["candidate"]["id"])
    assert saved["plan"]["actions"] == result["candidate"]["actions"]
    assert saved["plan"]["proposed"] == result["candidate"]["proposed"]
    assert saved["verification"]["plan_id"] == saved["plan"]["id"]
    assert saved["verification"]["status"] == "SAFE"
    assert saved["plan"]["revision"] == workspace["revision"]
    assert store.get(sid).plan.model_dump(mode="json") == saved["plan"]
    assert {p.id for p in store.history(sid)} == {source["id"], saved["plan"]["id"]}
    assert [v.model_dump(mode="json") for v in store.verifications(sid)] == [saved["verification"]]
    assert client.post("/api/synthesis/adopt", headers=headers, json=adoption(result)).status_code == 409


def test_auth_scope_malformed_and_unsupported_requests(api):
    client, store, _ = api
    headers, workspace, _, body = start(api)
    other, _, _, _ = start(api)
    assert client.post("/api/synthesis", json=body).status_code == 401
    assert client.post("/api/synthesis", headers=other, json=body).status_code == 409
    result = preview(client, headers, body)
    assert client.post("/api/synthesis/adopt", json=adoption(result)).status_code == 401
    assert client.post("/api/synthesis/adopt", headers=other, json=adoption(result)).status_code == 409
    for bad in [{**body, "max_candidates": 0}, {**body, "revision": 900},
                {**body, "uncertainties": [*body["uncertainties"], *body["uncertainties"]]}]:
        assert client.post("/api/synthesis", headers=headers, json=bad).status_code in (409, 422)
    forged = adoption(result)
    forged["balance_cents"] = 900000
    assert client.post("/api/synthesis/adopt", headers=headers, json=forged).status_code == 422
    forged = adoption(result)
    forged["candidate_fingerprint"] = "0" * 64
    assert client.post("/api/synthesis/adopt", headers=headers, json=forged).status_code == 409
    client.post("/api/plan", headers=headers, json={"include_conditional": True})
    body["plan_id"] = store.get(workspace["session_id"]).plan.id
    assert client.post("/api/synthesis", headers=headers, json=body).status_code == 422
    assert client.post("/api/sessions", json={"demo": False, "demo_variant": "resilient"}).status_code == 422


@pytest.mark.parametrize("operation", ["preview", "adopt"])
@pytest.mark.parametrize("race", ["revision", "active_plan", "source_readiness", "delete"])
def test_changes_during_computation_fail_closed(api, monkeypatch, operation, race):
    client, store, _ = api
    headers, workspace, _, body = start(api)
    result = preview(client, headers, body)
    sid = workspace["session_id"]
    name = "synthesize_plan" if operation == "preview" else "revalidate_candidate"
    original = getattr(synthesis, name)

    def changing(*args):
        computed = original(*args)
        if race == "delete":
            store.delete_session(sid)
        elif race == "revision":
            store.mutate(sid, lambda current: None)
        elif race == "source_readiness":
            store.mutate(sid, lambda current: setattr(current.documents[0], "status", "extracting"), invalidate=False)
        else:
            store.mutate(sid, lambda current: setattr(current.plan, "id", "replacement-plan"), invalidate=False)
        return computed

    monkeypatch.setattr(synthesis, name, changing)
    endpoint, payload = ("/api/synthesis", body) if operation == "preview" else ("/api/synthesis/adopt", adoption(result))
    response = client.post(endpoint, headers=headers, json=payload)
    assert response.status_code == (401 if race == "delete" else 409), response.text
    assert store.verifications(sid) == []


def test_failure_after_plan_projection_rolls_back_snapshot_plan_and_proof(api, monkeypatch):
    client, store, _ = api
    headers, workspace, _, body = start(api)
    result = preview(client, headers, body)
    sid = workspace["session_id"]
    before, rows = store.get(sid).model_dump_json(), counts(store, sid)
    original = store._save_verification

    def fail_after_insert(*args):
        original(*args)
        raise RuntimeError("Injected write failure after proof and daily series")

    monkeypatch.setattr(store, "_save_verification", fail_after_insert)
    with pytest.raises(RuntimeError, match="Injected write failure"):
        client.post("/api/synthesis/adopt", headers=headers, json=adoption(result))
    assert store.get(sid).model_dump_json() == before
    assert counts(store, sid) == rows


def test_concurrent_adoptions_have_exactly_one_winner(api, monkeypatch):
    client, store, _ = api
    headers, workspace, _, body = start(api)
    result = preview(client, headers, body)
    original = synthesis.revalidate_candidate
    barrier = Barrier(2)

    def synchronized(*args):
        checked = original(*args)
        barrier.wait(timeout=10)
        return checked

    monkeypatch.setattr(synthesis, "revalidate_candidate", synchronized)
    def adopt():
        return client.post("/api/synthesis/adopt", headers=headers, json=adoption(result)).status_code
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: adopt(), range(2)))
    assert sorted(results) == [200, 409]
    assert len(store.history(workspace["session_id"])) == 2
    assert len(store.verifications(workspace["session_id"])) == 1


@pytest.mark.parametrize("deletion", ["source", "reset", "session"])
def test_adopted_history_respects_deletion_and_variant_reset(api, deletion):
    client, store, _ = api
    headers, workspace, _, body = start(api)
    result = preview(client, headers, body)
    assert client.post("/api/synthesis/adopt", headers=headers, json=adoption(result)).status_code == 200
    if deletion == "source":
        response = client.delete("/api/documents/resilient-doc-3", headers=headers)
    elif deletion == "reset":
        response = client.post("/api/demo/reset", headers=headers)
        assert response.json()["demo_variant"] == "resilient"
        assert len(response.json()["documents"]) == 3
    else:
        response = client.delete("/api/session", headers=headers)
    assert response.status_code == 200, response.text
    assert counts(store, workspace["session_id"]) == [0, 0, 0, 0]
