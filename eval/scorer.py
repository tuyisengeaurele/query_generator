"""Execution accuracy scoring: run the predicted SQL and the gold SQL
against the same database, compare the result sets as unordered row sets.
This is the standard BIRD metric. It has a known limitation, documented in
the ablation report: a predicted query that is semantically correct but
returns columns in a different order, or with different aliases, can score
as a false negative under a strict set comparison."""

from __future__ import annotations

from sqlalchemy import Engine, text


def _run(engine: Engine, sql: str) -> set[tuple] | None:
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            return {tuple(row) for row in result.fetchall()}
    except Exception:
        return None


def execution_accuracy(engine: Engine, predicted_sql: str, gold_sql: str) -> bool:
    predicted_rows = _run(engine, predicted_sql)
    gold_rows = _run(engine, gold_sql)
    if predicted_rows is None or gold_rows is None:
        return False
    return predicted_rows == gold_rows
