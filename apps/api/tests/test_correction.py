from app.pipeline.correction import run_with_correction
from app.pipeline.schema_linking import FullSchemaLinker
from app.db.introspect import introspect_schema
from app.providers.base import ModelProvider


class ScriptedProvider(ModelProvider):
    name = "scripted"

    def __init__(self, responses: list[str]):
        self._responses = list(responses)
        self.calls: list[str] = []

    def generate(self, prompt: str) -> str:
        self.calls.append(prompt)
        return self._responses.pop(0)


def _linked_schema(engine):
    return FullSchemaLinker().link("question", introspect_schema(engine, use_cache=False))


def test_succeeds_on_first_attempt_when_sql_is_valid(sqlite_engine):
    provider = ScriptedProvider(["```sql\nSELECT id FROM members\n```"])
    schema = _linked_schema(sqlite_engine)

    final_sql, result, attempts = run_with_correction(
        question="list members",
        schema=schema,
        provider=provider,
        generate_initial_sql=lambda: "SELECT id FROM members",
        engine=sqlite_engine,
        dialect="sqlite",
        default_limit=200,
        timeout_seconds=5,
        max_retries=3,
    )

    assert result.success is True
    assert len(attempts) == 1
    assert attempts[0].success is True


def test_retries_after_database_error_and_then_succeeds(sqlite_engine):
    provider = ScriptedProvider(["SELECT id FROM members"])

    schema = _linked_schema(sqlite_engine)
    final_sql, result, attempts = run_with_correction(
        question="list members",
        schema=schema,
        provider=provider,
        generate_initial_sql=lambda: "SELECT id FROM memebrs",
        engine=sqlite_engine,
        dialect="sqlite",
        default_limit=200,
        timeout_seconds=5,
        max_retries=3,
    )

    assert result.success is True
    assert len(attempts) == 2
    assert attempts[0].success is False
    assert "memebrs" in attempts[0].sql or attempts[0].error is not None
    assert attempts[1].success is True


def test_exhausts_retries_and_returns_last_failed_attempt(sqlite_engine):
    provider = ScriptedProvider(
        ["SELECT id FROM memebrs", "SELECT id FROM memebrs", "SELECT id FROM memebrs"]
    )
    schema = _linked_schema(sqlite_engine)

    final_sql, result, attempts = run_with_correction(
        question="list members",
        schema=schema,
        provider=provider,
        generate_initial_sql=lambda: "SELECT id FROM memebrs",
        engine=sqlite_engine,
        dialect="sqlite",
        default_limit=200,
        timeout_seconds=5,
        max_retries=3,
    )

    assert result.success is False
    assert len(attempts) == 4
    assert all(a.success is False for a in attempts)


def test_retries_on_empty_result_when_question_implies_rows(sqlite_engine):
    provider = ScriptedProvider(["SELECT id FROM members"])
    schema = _linked_schema(sqlite_engine)

    final_sql, result, attempts = run_with_correction(
        question="how many members are there with id 999",
        schema=schema,
        provider=provider,
        generate_initial_sql=lambda: "SELECT id FROM members WHERE id = 999",
        engine=sqlite_engine,
        dialect="sqlite",
        default_limit=200,
        timeout_seconds=5,
        max_retries=3,
    )

    assert len(attempts) == 2
    assert attempts[0].success is False
