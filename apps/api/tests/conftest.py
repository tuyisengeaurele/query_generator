import pytest
from sqlalchemy import create_engine, text


@pytest.fixture
def sqlite_engine(tmp_path):
    db_path = tmp_path / "fixture.db"
    engine = create_engine(f"sqlite:///{db_path}")
    with engine.begin() as conn:
        conn.execute(
            text(
                "CREATE TABLE members ("
                "id INTEGER PRIMARY KEY, "
                "full_name TEXT NOT NULL, "
                "cooperative_id INTEGER"
                ")"
            )
        )
        conn.execute(
            text(
                "CREATE TABLE cooperatives ("
                "id INTEGER PRIMARY KEY, "
                "name TEXT NOT NULL"
                ")"
            )
        )
        conn.execute(text("INSERT INTO cooperatives (id, name) VALUES (1, 'Kigali Growers')"))
        conn.execute(
            text(
                "INSERT INTO members (id, full_name, cooperative_id) VALUES "
                "(1, 'Alice Uwase', 1), (2, 'Beatrice Mukamana', 1)"
            )
        )
    return engine
