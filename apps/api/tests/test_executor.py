from app.pipeline.executor import execute_sql


def test_execute_sql_returns_rows_on_success(sqlite_engine):
    result = execute_sql(sqlite_engine, "SELECT id, full_name FROM members ORDER BY id", timeout_seconds=5)
    assert result.success is True
    assert result.columns == ["id", "full_name"]
    assert result.rows[0]["full_name"] == "Alice Uwase"


def test_execute_sql_returns_error_on_bad_table(sqlite_engine):
    result = execute_sql(sqlite_engine, "SELECT * FROM not_a_real_table", timeout_seconds=5)
    assert result.success is False
    assert "not_a_real_table" in result.error


def test_execute_sql_returns_empty_rows_for_no_matches(sqlite_engine):
    result = execute_sql(sqlite_engine, "SELECT * FROM members WHERE id = 999", timeout_seconds=5)
    assert result.success is True
    assert result.rows == []
