"""End-to-end test: a real question runs through introspection, schema
linking, few-shot retrieval, prompt building, guardrails, and execution
against a real sqlite database, using a fake provider standing in for the
live model call."""

from fastapi.testclient import TestClient

from app.api.routes import query as query_route
from app.config import Settings
from app.main import app
from app.providers.base import ModelProvider


class FixedSqlProvider(ModelProvider):
    name = "fixed"

    def generate(self, prompt: str) -> str:
        assert "members" in prompt
        return "```sql\nSELECT full_name FROM members WHERE cooperative_id = 1 ORDER BY id\n```"


def test_full_pipeline_returns_correct_rows_for_a_real_question(monkeypatch, sqlite_engine):
    monkeypatch.setattr(query_route, "get_engine", lambda url: sqlite_engine)
    monkeypatch.setattr(query_route, "build_provider", lambda settings: FixedSqlProvider())
    monkeypatch.setattr(
        query_route,
        "get_settings",
        lambda: Settings(database_url="sqlite:///unused", model_provider="anthropic"),
    )

    client = TestClient(app)
    response = client.post("/query", json={"question": "Who are the members of Kigali Growers?"})

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["attempt_count"] == 1
    assert [row["full_name"] for row in body["rows"]] == ["Alice Uwase", "Beatrice Mukamana"]
    assert "LIMIT" in body["sql"]
