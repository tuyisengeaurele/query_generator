from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable

from app.pipeline.executor import ExecutionResult, execute_sql
from app.pipeline.guardrails import GuardrailViolation, enforce_guardrails
from app.pipeline.prompt import build_correction_prompt
from app.pipeline.schema_linking import LinkedSchema
from app.pipeline.sql_extract import extract_sql
from app.providers.base import ModelProvider

_ROWS_IMPLIED_PATTERN = re.compile(r"\b(how many|list|show|which|what are|count)\b", re.IGNORECASE)


@dataclass
class Attempt:
    sql: str
    success: bool
    error: str | None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def looks_like_rows_were_expected(question: str, result: ExecutionResult) -> bool:
    """Heuristic: an empty result set is suspicious, not necessarily wrong,
    when the question phrasing implies rows should come back."""
    if not result.success or result.rows:
        return False
    return bool(_ROWS_IMPLIED_PATTERN.search(question))


def run_with_correction(
    *,
    question: str,
    schema: LinkedSchema,
    provider: ModelProvider,
    generate_initial_sql: Callable[[], str],
    engine,
    dialect: str,
    default_limit: int,
    timeout_seconds: int,
    max_retries: int,
) -> tuple[str, ExecutionResult, list[Attempt]]:
    """Runs the generate -> guard -> execute cycle, and on a database error
    or an empty-result-when-rows-implied case, re-prompts the model with the
    error attached. Capped at max_retries corrections beyond the first
    attempt. Returns the final SQL, its execution result, and the full
    attempt trace."""
    attempts: list[Attempt] = []
    raw_sql = generate_initial_sql()

    for attempt_number in range(max_retries + 1):
        try:
            guarded_sql = enforce_guardrails(raw_sql, dialect=dialect, default_limit=default_limit)
        except GuardrailViolation as exc:
            attempts.append(Attempt(sql=raw_sql, success=False, error=str(exc)))
            if attempt_number == max_retries:
                return raw_sql, ExecutionResult(success=False, error=str(exc)), attempts
            raw_sql = extract_sql(
                provider.generate(build_correction_prompt(question, schema, raw_sql, str(exc)))
            )
            continue

        result = execute_sql(engine, guarded_sql, timeout_seconds)
        needs_retry = not result.success or looks_like_rows_were_expected(question, result)
        attempts.append(Attempt(sql=guarded_sql, success=result.success and not needs_retry, error=result.error))

        if not needs_retry:
            return guarded_sql, result, attempts

        if attempt_number == max_retries:
            return guarded_sql, result, attempts

        error_text = result.error or "query executed but returned no rows for a question that implies rows exist"
        raw_sql = extract_sql(provider.generate(build_correction_prompt(question, schema, guarded_sql, error_text)))

    # Unreachable: the loop always returns within max_retries + 1 iterations.
    raise RuntimeError("correction loop exited without a result")
