"""Explicit mocked model checks plus real bounded local PDF rendering; no live calls."""
import io
import json

import httpx
import pytest
from PIL import Image
from pypdf import PdfWriter

from clausegraph import document_images
from clausegraph.config import Settings
from clausegraph.demo import load_demo
from clausegraph.providers import ProviderError, Providers
from clausegraph.schemas import DocumentPage


def reply(payload, finish="stop"):
    return httpx.Response(200, json={"choices": [{"finish_reason": finish, "message": {"content": json.dumps(payload)}}]})


def settings(**overrides):
    return Settings(_env_file=None, nvidia_api_key="synthetic-test-key", gemini_api_key="",
        provider_retries=0, **overrides)


def pdf_bytes(count=2, width=600, height=800):
    writer = PdfWriter()
    for _ in range(count):
        writer.add_blank_page(width, height)
    stream = io.BytesIO()
    writer.write(stream)
    return stream.getvalue()


def test_nvidia_default_separate_model_and_json_protocol():
    _, documents, rules = load_demo()
    calls = []
    def handle(request):
        body = json.loads(request.content)
        calls.append(body)
        assert request.url.host == "integrate.api.nvidia.com"
        assert body["model"] == "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning"
        assert body["reasoning_budget"] == 1024 and body["max_tokens"] == 8192
        assert "guided_json" not in body and "response_format" not in body
        assert "source_document" in body["messages"][1]["content"][0]["text"]
        return reply({"checks": [{"rule_id": rules[0].id, "supported": False, "reason": "Synthetic disagreement"}]})
    providers = Providers(settings(), httpx.MockTransport(handle))
    assert providers.settings.evidence_provider == "nvidia"
    assert providers.settings.nvidia_model != providers.evidence_model
    assert providers.verify(documents[0], [rules[0]])[0].supported is False
    assert len(calls) == 1
    statuses = providers.statuses()
    assert statuses[1].name == "NVIDIA Nemotron evidence" and statuses[1].configured
    assert not any(status.name == "Gemini" for status in statuses)


@pytest.mark.parametrize("checks", [[], [{"rule_id": "unknown", "supported": True, "reason": "invalid"}],
    [{"rule_id": "rule-rent", "supported": True, "reason": "same"}] * 2])
def test_verifier_missing_unknown_or_duplicate_checks_fail_closed(checks):
    _, documents, rules = load_demo()
    providers = Providers(settings(), httpx.MockTransport(lambda request: reply({"checks": checks})))
    with pytest.raises(ProviderError, match="missing, duplicate or unknown"):
        providers.verify(documents[0], [rules[0]])


@pytest.mark.parametrize("response", [reply({"checks": []}, "length"), reply({"checks": []}, "content_filter"),
    httpx.Response(200, json={"choices": []}),
    httpx.Response(200, json={"choices": [{"finish_reason": "stop", "message": {"content": "not JSON"}}]})])
def test_incomplete_or_malformed_evidence_is_never_accepted(response):
    _, documents, rules = load_demo()
    providers = Providers(settings(), httpx.MockTransport(lambda request: response))
    with pytest.raises(ProviderError):
        providers.verify(documents[0], [rules[0]])


def test_nvidia_failure_never_falls_back_to_configured_gemini():
    _, documents, rules = load_demo()
    configuration = settings()
    configuration.gemini_api_key = "synthetic-unused-key"
    calls = []
    def handle(request):
        calls.append(request.url.host)
        return httpx.Response(429, text="sensitive provider error not for display")
    providers = Providers(configuration, httpx.MockTransport(handle))
    with pytest.raises(ProviderError, match="HTTP 429") as exc:
        providers.verify(documents[0], [rules[0]])
    assert "sensitive" not in str(exc.value)
    assert calls == ["integrate.api.nvidia.com"]


def test_gemini_requires_explicit_selection_and_its_own_key():
    _, documents, rules = load_demo()
    providers = Providers(settings(evidence_provider="gemini"), httpx.MockTransport(lambda request: pytest.fail("No request without key")))
    assert providers.statuses()[1].name == "Gemini"
    with pytest.raises(ProviderError, match="GEMINI_API_KEY"):
        providers.verify(documents[0], [rules[0]])
    with pytest.raises(ValueError):
        settings(evidence_provider="automatic-paid-fallback")


def test_real_pdf_rendering_is_numbered_rgb_and_bounded():
    images = document_images.render_pdf_pages(pdf_bytes(), [2])
    assert [number for number, _ in images] == [2]
    with Image.open(io.BytesIO(images[0][1])) as image:
        assert image.mode == "RGB" and max(image.size) <= 1600
    assert len(images[0][1]) <= document_images.MAX_IMAGE_BYTES


@pytest.mark.parametrize("numbers", [[0], [True], [1, 1], [1, 2, 3, 4, 5], []])
def test_bad_render_page_requests_rejected(numbers):
    with pytest.raises(ValueError):
        document_images.render_pdf_pages(pdf_bytes(), numbers)


def test_renderer_rejects_bad_pdf_excess_pages_and_expired_deadline(monkeypatch):
    with pytest.raises(ValueError, match="Invalid or oversized"):
        document_images.render_pdf_pages(b"not pdf", [1])
    with pytest.raises(ValueError, match="safe limits"):
        document_images.render_pdf_pages(pdf_bytes(5))
    monkeypatch.setattr(document_images, "RENDER_TIMEOUT_SECONDS", 0.0)
    with pytest.raises(ValueError, match="timed out"):
        document_images.render_pdf_pages(pdf_bytes(), [1])


def test_vision_sends_only_missing_native_page_and_checks_original_images():
    _, documents, rules = load_demo()
    document = documents[0].model_copy(deep=True)
    document.media_type = "application/pdf"
    document.pages = [DocumentPage(page=1, text="Native source text remains intact. " * 3), DocumentPage(page=2, text="")]
    original = pdf_bytes()
    calls = []
    def handle(request):
        body = json.loads(request.content)
        content = body["messages"][1]["content"]
        calls.append(content)
        assert content[1]["text"] == "Original source page 2:"
        assert content[2]["image_url"]["url"].startswith("data:image/jpeg;base64,")
        if "Transcribe original" in content[0]["text"]:
            return reply({"pages": [{"page": 2, "text": "SYNTHETIC transcription $1600.00"}]})
        return reply({"checks": [{"rule_id": rules[0].id, "supported": True, "reason": "Mock image check"}]})
    providers = Providers(settings(), httpx.MockTransport(handle))
    pages = providers.vision(document, original)
    assert len(pages) == 1 and pages[0].page == 2
    assert document.pages[0].text.startswith("Native source")
    rule = rules[0].model_copy(deep=True)
    rule.evidence[0].page = 2
    providers.verify(document, [rule], original)
    assert len(calls) == 2


def test_vision_rejects_invented_page_numbers():
    _, documents, _ = load_demo()
    document = documents[0].model_copy(deep=True)
    document.pages = [DocumentPage(page=1, text="")]
    providers = Providers(settings(), httpx.MockTransport(lambda request: reply({"pages": [{"page": 9, "text": "invented"}]})))
    with pytest.raises(ProviderError, match="page numbers"):
        providers.vision(document, pdf_bytes(1))


def test_evidence_smoke_tests_selected_model_only_with_small_budget():
    seen = []
    def handle(request):
        body = json.loads(request.content)
        seen.append(body)
        return reply({"ok": True})
    configuration = settings()
    configuration.gemini_api_key = "unused-key"
    providers = Providers(configuration, httpx.MockTransport(handle))
    statuses = providers.smoke()
    assert len(seen) == 2
    assert seen[1]["reasoning_budget"] == 0 and seen[1]["max_tokens"] == 128
    assert statuses[1].mode == "live" and "succeeded" in statuses[1].detail
