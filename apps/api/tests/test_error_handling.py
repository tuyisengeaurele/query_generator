from fastapi.testclient import TestClient

from app.api.routes import query as query_route
from app.config import Settings
from app.main import app
from app.providers.base import ModelProvider, ProviderError


class AlwaysFailsProvider(ModelProvider):
    name = "always-fails"

    def generate(self, prompt: str) -> str:
        raise ProviderError("simulated provider outage")


def test_provider_error_returns_clean_502(monkeypatch, sqlite_engine):
    monkeypatch.setattr(query_route, "get_engine", lambda url: sqlite_engine)
    monkeypatch.setattr(query_route, "build_provider", lambda settings: AlwaysFailsProvider())
    monkeypatch.setattr(
        query_route, "get_settings", lambda: Settings(database_url="sqlite:///unused")
    )

    client = TestClient(app, raise_server_exceptions=False)
    response = client.post("/query", json={"question": "list members"})

    assert response.status_code == 502
    body = response.json()
    assert body["detail"] == "the model provider request failed"
    assert "Traceback" not in response.text
