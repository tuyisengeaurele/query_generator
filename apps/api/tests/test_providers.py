import httpx
import pytest

from app.config import Settings
from app.providers.anthropic_provider import AnthropicProvider
from app.providers.base import ModelProvider, ProviderError
from app.providers.factory import build_provider
from app.providers.groq import GroqProvider
from app.providers.ollama import OllamaProvider


class FakeProvider(ModelProvider):
    name = "fake"

    def __init__(self, response: str):
        self._response = response

    def generate(self, prompt: str) -> str:
        return self._response


def test_fake_provider_satisfies_interface():
    provider = FakeProvider("SELECT 1")
    assert isinstance(provider, ModelProvider)
    assert provider.generate("any prompt") == "SELECT 1"


def test_ollama_provider_generate_success(monkeypatch):
    def fake_post(url, json, timeout):
        assert url.endswith("/api/generate")
        assert json["model"] == "llama3.1"
        request = httpx.Request("POST", url)
        return httpx.Response(200, json={"response": "SELECT * FROM members"}, request=request)

    monkeypatch.setattr(httpx, "post", fake_post)
    provider = OllamaProvider(host="http://localhost:11434", model="llama3.1")
    assert provider.generate("question") == "SELECT * FROM members"


def test_ollama_provider_wraps_http_errors(monkeypatch):
    def fake_post(url, json, timeout):
        raise httpx.ConnectError("connection refused")

    monkeypatch.setattr(httpx, "post", fake_post)
    provider = OllamaProvider(host="http://localhost:11434", model="llama3.1")
    with pytest.raises(ProviderError):
        provider.generate("question")


def test_groq_provider_generate_success(monkeypatch):
    def fake_post(url, headers, json, timeout):
        assert headers["Authorization"] == "Bearer test-key"
        request = httpx.Request("POST", url)
        payload = {"choices": [{"message": {"content": "SELECT 1"}}]}
        return httpx.Response(200, json=payload, request=request)

    monkeypatch.setattr(httpx, "post", fake_post)
    provider = GroqProvider(api_key="test-key", model="llama-3.3-70b-versatile")
    assert provider.generate("question") == "SELECT 1"


def test_anthropic_provider_generate_success(monkeypatch):
    class FakeTextBlock:
        type = "text"
        text = "SELECT * FROM cooperatives"

    class FakeMessage:
        content = [FakeTextBlock()]

    class FakeMessages:
        def create(self, **kwargs):
            assert kwargs["model"] == "claude-sonnet-5"
            return FakeMessage()

    class FakeClient:
        def __init__(self, api_key):
            self.messages = FakeMessages()

    monkeypatch.setattr("app.providers.anthropic_provider.anthropic.Anthropic", FakeClient)
    provider = AnthropicProvider(api_key="test-key", model="claude-sonnet-5")
    assert provider.generate("question") == "SELECT * FROM cooperatives"


def test_factory_builds_correct_provider_type():
    settings = Settings(model_provider="ollama", ollama_host="http://localhost:11434", ollama_model="llama3.1")
    provider = build_provider(settings)
    assert isinstance(provider, OllamaProvider)


def test_factory_raises_on_unknown_provider():
    settings = Settings(model_provider="not-a-real-provider")
    with pytest.raises(ValueError):
        build_provider(settings)
