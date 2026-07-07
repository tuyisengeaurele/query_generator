from fastapi.testclient import TestClient

from app.api.routes import schema as schema_route
from app.config import Settings
from app.main import app


def test_schema_endpoint_returns_tables_and_columns(monkeypatch, sqlite_engine):
    monkeypatch.setattr(schema_route, "get_engine", lambda url: sqlite_engine)
    monkeypatch.setattr(
        schema_route, "get_settings", lambda: Settings(database_url="sqlite:///unused")
    )

    client = TestClient(app)
    response = client.get("/schema")

    assert response.status_code == 200
    body = response.json()
    table_names = {t["name"] for t in body}
    assert "members" in table_names
    assert "cooperatives" in table_names
