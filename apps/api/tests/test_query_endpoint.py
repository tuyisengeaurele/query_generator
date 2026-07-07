from fastapi.testclient import TestClient

from app.api.routes import query as query_route
from app.config import Settings
from app.main import app
from app.providers.base import ModelProvider


class OneShotProvider(ModelProvider):
    name = "test-provider"

    def generate(self, prompt: str) -> str:
        return "```sql\nSELECT id, full_name FROM members ORDER BY id\n```"


def test_query_endpoint_returns_sql_rows_and_trace(monkeypatch, sqlite_engine):
    monkeypatch.setattr(query_route, "get_engine", lambda url: sqlite_engine)
    monkeypatch.setattr(query_route, "build_provider", lambda settings: OneShotProvider())
    monkeypatch.setattr(
        query_route,
        "get_settings",
        lambda: Settings(database_url="sqlite:///unused", model_provider="anthropic"),
    )

    client = TestClient(app)
    response = client.post("/query", json={"question": "list all members"})

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "SELECT" in body["sql"]
    assert body["model"] == "test-provider"
    assert body["attempt_count"] == 1
    assert isinstance(body["latency_ms"], int)
    assert body["rows"][0]["full_name"] == "Alice Uwase"
