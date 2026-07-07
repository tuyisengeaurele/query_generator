import pytest

from app.pipeline.guardrails import GuardrailViolation, enforce_guardrails


def test_valid_select_passes_unchanged_when_limit_present():
    sql = "SELECT id FROM members LIMIT 10"
    result = enforce_guardrails(sql, dialect="sqlite", default_limit=200)
    assert "LIMIT 10" in result
    assert result.count("LIMIT") == 1


def test_injects_limit_when_missing():
    sql = "SELECT id FROM members"
    result = enforce_guardrails(sql, dialect="sqlite", default_limit=200)
    assert "LIMIT 200" in result


@pytest.mark.parametrize(
    "sql",
    [
        "INSERT INTO members (id) VALUES (1)",
        "UPDATE members SET full_name = 'x' WHERE id = 1",
        "DELETE FROM members WHERE id = 1",
        "DROP TABLE members",
        "ALTER TABLE members ADD COLUMN x TEXT",
        "CREATE TABLE evil (id INTEGER)",
        "TRUNCATE members",
        "ATTACH DATABASE 'other.db' AS other",
    ],
)
def test_rejects_ddl_and_dml(sql):
    with pytest.raises(GuardrailViolation):
        enforce_guardrails(sql, dialect="sqlite", default_limit=200)


def test_rejects_multiple_statements():
    sql = "SELECT id FROM members; DROP TABLE members;"
    with pytest.raises(GuardrailViolation):
        enforce_guardrails(sql, dialect="sqlite", default_limit=200)


def test_rejects_comment_smuggled_statement():
    sql = "SELECT id FROM members; -- ok\nDROP TABLE members"
    with pytest.raises(GuardrailViolation):
        enforce_guardrails(sql, dialect="sqlite", default_limit=200)


def test_rejects_insert_hidden_in_cte():
    sql = "WITH x AS (INSERT INTO members (id) VALUES (1) RETURNING id) SELECT * FROM x"
    with pytest.raises(GuardrailViolation):
        enforce_guardrails(sql, dialect="sqlite", default_limit=200)


def test_rejects_empty_sql():
    with pytest.raises(GuardrailViolation):
        enforce_guardrails("", dialect="sqlite", default_limit=200)


def test_rejects_unparseable_sql():
    with pytest.raises(GuardrailViolation):
        enforce_guardrails("SELEKT * FORM members !!!", dialect="sqlite", default_limit=200)
