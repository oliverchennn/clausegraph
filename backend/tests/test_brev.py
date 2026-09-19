"""Private optional text inference; every provider call here is mocked."""
import json

import httpx
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from clausegraph.api import create_app
from clausegraph.config import Settings
from clausegraph.demo import load_demo
from clausegraph.providers import ProviderError, Providers
from clausegraph.storage import Originals, Store
from clausegraph.worker import run_once
from test_api import PAYMENT_TEXT, start, transport_handler


def settings(**overrides):
    return Settings(_env_file=None, provider_retries=0, **overrides)


def reply(content, finish="stop"):
    return httpx.Response(200, json={"choices": [{"finish_reason": finish, "message": {"content": content}}]})


@pytest.mark.parametrize("url", ["https://public.example/v1", "http://0.0.0.0:8000/v1",
    "http://127.0.0.1:8000", "http://secret@localhost/v1", "http://localhost/v1?key=secret",
    "http://localhost/v1#fragment", "http://localhost.example/v1"])
def test_brev_rejects_public_or_credential_bearing_urls(url):
    with pytest.raises(ValidationError, match="private SSH tunnel"):
        settings(brev_nim_base_url=url)


@pytest.mark.parametrize("url", ["http://127.0.0.1:18000/v1", "http://localhost:18000/v1/", "http://[::1]:18000/v1"])
def test_brev_accepts_loopback_tunnels(url):
    assert settings(brev_nim_base_url=url).brev_nim_base_url == url


def test_brev_text_keeps_hosted_evidence_and_secrets_separate():
    scenario, documents, rules = load_demo()
    calls = []
    def handle(request):
        calls.append(request)
        body = json.loads(request.content)
        if request.url.host == "127.0.0.1":
            assert "authorization" not in request.headers
            assert body["model"] == "my-nim-model"
            assert "guided_json" not in body and "response_format" not in body
            assert "schema" in body["messages"][0]["content"]
            return reply(json.dumps({"rules": [], "events": [], "actions": []}))
        assert request.url.host == "integrate.api.nvidia.com"
        assert request.headers["authorization"] == "Bearer hosted-only-key"
        assert body["model"] == "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning"
        return reply(json.dumps({"checks": [{"rule_id": rules[0].id, "supported": False, "reason": "Synthetic test"}]}))
    providers = Providers(settings(text_provider="brev", brev_nim_model="my-nim-model", nvidia_api_key="hosted-only-key"),
                          httpx.MockTransport(handle))
    providers.extract(documents[0], scenario)
    providers.verify(documents[0], [rules[0]])
    assert len(calls) == 2
    assert providers.statuses()[0].name == "Brev-hosted Nemotron"
    assert providers.statuses()[0].configured
    assert providers.statuses()[1].name == "NVIDIA Nemotron evidence"


def test_hosted_default_remains_keyed_and_schema_constrained():
    def handle(request):
        assert request.headers["authorization"] == "Bearer hosted-key"
        assert request.url.host == "integrate.api.nvidia.com"
        assert json.loads(request.content)["guided_json"] == {"type": "object"}
        return reply("{}")
    providers = Providers(settings(nvidia_api_key="hosted-key", brev_nim_model="unused"), httpx.MockTransport(handle))
    assert providers._nvidia("Synthetic", {}, {"type": "object"}) == "{}"


def test_missing_brev_model_does_not_fall_back_to_hosted():
    providers = Providers(settings(text_provider="brev", nvidia_api_key="unused-key"),
                          httpx.MockTransport(lambda request: pytest.fail("No request allowed")))
    assert not providers.statuses()[0].configured
    with pytest.raises(ProviderError, match="BREV_NIM_MODEL"):
        providers._nvidia("Synthetic", {})


@pytest.mark.parametrize("finish", ["length", "tool_calls", "content_filter", None])
def test_incomplete_brev_outputs_fail_closed(finish):
    providers = Providers(settings(text_provider="brev", brev_nim_model="test"),
                          httpx.MockTransport(lambda request: reply("{}", finish)))
    with pytest.raises(ProviderError):
        providers._nvidia("Synthetic", {})


@pytest.mark.parametrize("response", [httpx.Response(503, text="secret response"),
    httpx.Response(302, headers={"Location": "https://other.example"}), reply("not JSON")])
def test_brev_errors_do_not_fall_back_or_compile(response):
    calls = []
    def handle(request):
        calls.append(request)
        assert request.url.host == "127.0.0.1"
        return response
    providers = Providers(settings(text_provider="brev", brev_nim_model="test", nvidia_api_key="hosted-secret"),
                          httpx.MockTransport(handle))
    scenario, documents, _ = load_demo()
    with pytest.raises(ProviderError) as error:
        providers.extract(documents[0], scenario)
    assert "secret" not in str(error.value)
    assert len(calls) == 1


def test_brev_does_not_use_environment_proxy_or_hosted_credentials(monkeypatch):
    clients = []
    original = httpx.Client
    def client(**kwargs):
        clients.append(kwargs["trust_env"])
        return original(**kwargs)
    monkeypatch.setattr(httpx, "Client", client)
    providers = Providers(settings(text_provider="brev", brev_nim_model="test"),
                          httpx.MockTransport(lambda request: reply("{}")))
    providers._nvidia("Synthetic", {})
    assert clients == [False]


@pytest.fixture
def api(tmp_path):
    config = settings(database_url=f"sqlite:///{tmp_path / 'test.db'}", local_storage_path=tmp_path / "originals",
                      text_provider="brev", brev_nim_model="test", nvidia_api_key="hosted-only-key")
    store, originals = Store(config), Originals(config)
    providers = Providers(config, httpx.MockTransport(transport_handler))
    with TestClient(create_app(config, store, providers, originals)) as client:
        yield client, store, providers, originals
    store.engine.dispose()


def upload(client, headers, text_provider=None, consent=True):
    data = {"consent": str(consent).lower(), "consent_provider": "nvidia"}
    if text_provider is not None:
        data["consent_text_provider"] = text_provider
    return client.post("/api/documents", headers=headers, data=data,
                       files={"file": ("test.txt", PAYMENT_TEXT.encode(), "text/plain")})


@pytest.mark.parametrize("text_provider", [None, "nvidia", "unknown"])
def test_brev_upload_requires_named_consent_before_storage(api, text_provider):
    client, store, _, _ = api
    headers, workspace = start(client, demo=False)
    assert upload(client, headers, text_provider).status_code == 409
    assert store.get(workspace["session_id"]).documents == []


def test_brev_upload_without_processing_consent_stays_local(api):
    client, store, providers, originals = api
    headers, _ = start(client, demo=False)
    providers.transport = httpx.MockTransport(lambda request: pytest.fail("No processing consent"))
    response = upload(client, headers, consent=False)
    assert response.status_code == 201 and response.json()["job"] is None
    assert not run_once(store, originals, providers)


def test_brev_pipeline_preserves_review_and_money_gates(api):
    client, store, providers, originals = api
    headers, workspace = start(client, demo=False)
    response = upload(client, headers, "brev")
    assert response.status_code == 201
    assert run_once(store, originals, providers)
    saved = store.get(workspace["session_id"])
    assert saved.jobs[0].status == "completed"
    assert saved.rules[0].amount_cents == 12345
    assert saved.rules[0].review_status.value == "pending"
    assert saved.rules[0].approval_status.value == "not_required"
    assert not saved.scenario.events  # Model output never creates reviewed cash.


@pytest.mark.parametrize("field,value", [("text_provider", "nvidia"), ("brev_nim_model", "other-model"),
    ("brev_nim_base_url", "http://127.0.0.1:18001/v1"), ("nvidia_base_url", "https://other.example/v1")])
def test_queued_work_rejects_routing_changes_before_sending(api, field, value):
    client, store, providers, originals = api
    headers, workspace = start(client, demo=False)
    response = upload(client, headers, "brev").json()
    setattr(providers.settings, field, value)
    providers.transport = httpx.MockTransport(lambda request: pytest.fail("Changed consent must not send data"))
    assert run_once(store, originals, providers)
    job = store.get_job(workspace["session_id"], response["job"]["id"])
    assert job.status == "failed" and "changed after consent" in job.error


def test_failed_job_can_be_reconsented_for_new_route(api):
    client, store, providers, originals = api
    headers, _ = start(client, demo=False)
    upload(client, headers, "brev")
    providers.settings.brev_nim_model = "new-model"
    assert run_once(store, originals, providers)
    retry = upload(client, headers, "brev")
    assert retry.status_code == 201 and retry.json()["duplicate"]
    assert run_once(store, originals, providers)
    assert client.get("/api/workspace", headers=headers).json()["jobs"][0]["status"] == "completed"


def test_brev_draft_requires_named_consent_and_remains_unsent(api):
    client, _, providers, _ = api
    headers, workspace = start(client)
    action_id = workspace["scenario"]["actions"][0]["id"]
    url = f"/api/actions/{action_id}/draft"
    providers.transport = httpx.MockTransport(lambda request: reply("Synthetic draft, not sent."))
    assert client.post(url, headers=headers, json={}).status_code == 200
    assert client.post(url, headers=headers, json={"use_provider": True}).status_code == 403
    assert client.post(url, headers=headers, json={"use_provider": True, "consent": True}).status_code == 409
    response = client.post(url, headers=headers, json={"use_provider": True, "consent": True, "consent_text_provider": "brev"})
    assert response.status_code == 200 and response.json()["sent"] is False


def test_brev_smoke_uses_text_route_without_hosted_key():
    providers = Providers(settings(text_provider="brev", brev_nim_model="test"),
                          httpx.MockTransport(lambda request: reply('{"ok":true}')))
    statuses = providers.smoke()
    assert "succeeded" in statuses[0].detail
    assert not statuses[1].configured
