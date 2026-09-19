"""Authenticated, revision-scoped, read-only queue and source deletion integration."""
from fastapi.testclient import TestClient
import pytest

from clausegraph.api import create_app
from clausegraph.config import Settings
from clausegraph.storage import Store


@pytest.fixture
def api(tmp_path):
    settings = Settings(_env_file=None, database_url=f"sqlite:///{tmp_path / 'review.db'}",
        local_storage_path=tmp_path / "originals", nvidia_api_key="", gemini_api_key="",
        elevenlabs_api_key="", spaces_bucket="", spaces_access_key_id="", spaces_secret_access_key="")
    store = Store(settings)
    with TestClient(create_app(settings=settings, store=store)) as client:
        yield client, store
    store.engine.dispose()


def start(client, demo=True):
    workspace = client.post("/api/sessions", json={"demo": demo}).json()
    return {"Authorization": f"Bearer {workspace['session_id']}"}, workspace


def test_get_does_not_optimize_mutate_or_write_history(api, monkeypatch):
    import clausegraph.engine as engine
    client, store = api
    headers, workspace = start(client)
    plan = client.post("/api/plan", headers=headers, json={}).json()
    before = store.get(workspace["session_id"]).model_dump(mode="json")
    def forbidden(*args, **kwargs):
        pytest.fail("Review queue must not optimize or persist")
    monkeypatch.setattr(engine, "optimize", forbidden)
    monkeypatch.setattr(store, "mutate", forbidden)
    monkeypatch.setattr(store, "save_verification", forbidden)
    first = client.get("/api/review-queue", headers=headers)
    assert first.status_code == 200
    assert client.get("/api/review-queue", headers=headers).json() == first.json()
    assert first.json()["revision"] == before["revision"]
    assert store.get(workspace["session_id"]).model_dump(mode="json") == before
    assert client.get("/api/history", headers=headers).json() == [plan]
    assert client.get("/api/verifications", headers=headers).json() == []
    assert "no-store" in first.headers["cache-control"]


def test_private_sessions_and_empty_queue(api):
    client, _ = api
    headers, _ = start(client)
    other, _ = start(client, demo=False)
    assert client.get("/api/review-queue").status_code == 401
    assert client.get("/api/review-queue", headers=headers).json()["items"]
    assert client.get("/api/review-queue", headers=other).json()["items"] == []
    client.delete("/api/session", headers=headers)
    assert client.get("/api/review-queue", headers=headers).status_code == 401
    assert client.get("/api/review-queue", headers=other).status_code == 200


def test_review_save_refreshes_revision_and_removes_only_resolved_task(api):
    client, _ = api
    headers, _ = start(client)
    response = client.patch("/api/rules/rule-rent", headers=headers, json={"review_status": "pending"})
    assert response.status_code == 200, response.text
    old = client.get("/api/review-queue", headers=headers).json()
    assert old["items"][0]["subject_id"] == "rule-rent"
    response = client.patch("/api/rules/rule-rent", headers=headers, json={"review_status": "reviewed"})
    assert response.status_code == 200, response.text
    new = client.get("/api/review-queue", headers=headers).json()
    assert new["revision"] > old["revision"]
    assert [entry["subject_id"] for entry in new["items"]] == ["rule-assistance"]


def test_failed_review_keeps_task_and_revision(api):
    client, _ = api
    headers, _ = start(client)
    client.patch("/api/rules/rule-rent", headers=headers, json={"review_status": "pending"})
    before = client.get("/api/review-queue", headers=headers).json()
    invalid = client.patch("/api/rules/rule-rent", headers=headers,
        json={"review_status": "reviewed", "evidence_confirmed": True})
    assert invalid.status_code == 422
    assert client.get("/api/review-queue", headers=headers).json() == before


def test_deleted_sources_leave_no_quotes_but_retained_expense_is_visible(api):
    client, _ = api
    headers, _ = start(client)
    deleted = client.delete("/api/documents/doc-1", headers=headers)
    assert deleted.status_code == 200, deleted.text
    queue = client.get("/api/review-queue", headers=headers).json()
    rent = next(entry for entry in queue["items"] if entry["subject_id"] == "rent")
    assert rent["evidence"] == [] and rent["rule_ids"] == [] and rent["missing_source"]
    assert rent["title"] == "Expense awaiting source review"
    assert "Harbor House" not in str(queue) and "1,600.00" not in str(queue)
    client.post("/api/demo/reset", headers=headers)
    assert [entry["subject_id"] for entry in client.get("/api/review-queue", headers=headers).json()["items"]] == ["rule-assistance"]
