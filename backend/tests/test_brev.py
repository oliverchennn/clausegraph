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
from clausegraph.schemas import DocumentPage, ExtractionResult
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
            assert "guided_json" not in body
            assert body["response_format"] == {"type": "json_schema", "json_schema": {
                "name": "clausegraph_response", "strict": True, "schema": ExtractionResult.model_json_schema()}}
            assert body["chat_template_kwargs"] == {"enable_thinking": True}
            assert body["thinking_token_budget"] == 2048
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
        body = json.loads(request.content)
        assert body["guided_json"] == {"type": "object"}
        assert body["response_format"] == {"type": "json_object"}
        assert "chat_template_kwargs" not in body
        assert "thinking_token_budget" not in body
        return reply("{}")
    providers = Providers(settings(nvidia_api_key="hosted-key", brev_nim_model="unused"), httpx.MockTransport(handle))
    assert providers._nvidia("Synthetic", {}, {"type": "object"}) == "{}"


@pytest.mark.parametrize("max_tokens,budget", [(128, 64), (8192, 2048)])
def test_brev_structured_reasoning_leaves_room_for_final_json(max_tokens, budget):
    def handle(request):
        body = json.loads(request.content)
        assert body["thinking_token_budget"] == budget < body["max_tokens"]
        assert body["chat_template_kwargs"] == {"enable_thinking": True}
        assert body["response_format"]["json_schema"]["schema"] == {"type": "object"}
        return reply("{}")
    provider = Providers(settings(text_provider="brev", brev_nim_model="test"), httpx.MockTransport(handle))
    assert provider._nvidia("Return JSON.", {}, {"type": "object"}, max_tokens=max_tokens) == "{}"


def test_brev_plain_text_reserves_output_budget_without_forcing_json():
    def handle(request):
        body = json.loads(request.content)
        assert "response_format" not in body and "guided_json" not in body
        assert "thinking_token_budget" not in body
        # Reproduce a reasoning-capable server exhausting its combined token budget.
        if body.get("chat_template_kwargs", {}).get("enable_thinking") is not False:
            return reply("", finish="length")
        return reply("Synthetic draft, not sent.")
    providers = Providers(settings(text_provider="brev", brev_nim_model="test"), httpx.MockTransport(handle))
    assert providers._nvidia("Write a plain text draft.", {}) == "Synthetic draft, not sent."


def test_brev_source_spans_preserve_unicode_offsets_versions_and_original_document():
    scenario, documents, _ = load_demo()
    document = documents[0].model_copy(deep=True)
    document.version = 3
    document.pages = [DocumentPage(page=2, text="\r\nCaf\u00e9 \U0001f4b5 $12.00\r\n\r\nRepeat\nRepeat\n  ")]
    before = document.model_dump(mode="json")
    captured = []
    def handle(request):
        source = json.loads(json.loads(request.content)["messages"][1]["content"])["source_document"]
        captured.extend(source["pages"][0]["evidence_spans"])
        assert "text" not in source["pages"][0]  # Do not double the source text/token budget.
        return reply('{"rules": [], "events": [], "actions": []}')
    provider = Providers(settings(text_provider="brev", brev_nim_model="test"), httpx.MockTransport(handle))
    provider.extract(document, scenario)
    assert document.model_dump(mode="json") == before
    assert [span["quote"] for span in captured] == ["Caf\u00e9 \U0001f4b5 $12.00", "Repeat", "Repeat"]
    assert [(span["char_start"], span["char_end"]) for span in captured] == [(2, 15), (19, 25), (26, 32)]
    for span in captured:
        assert span["document_id"] == document.id and span["version"] == 3 and span["page"] == 2
        assert document.pages[0].text[span["char_start"]:span["char_end"]] == span["quote"]


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
