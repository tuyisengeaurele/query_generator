from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.pipeline.timeout import StatementTimeoutError, run_with_timeout, set_postgres_statement_timeout


@dataclass
class ExecutionResult:
    success: bool
    columns: list[str] | None = None
    rows: list[dict] | None = None
    error: str | None = None


def execute_sql(engine: Engine, sql: str, timeout_seconds: int) -> ExecutionResult:
    is_postgres = engine.url.get_backend_name().startswith("postgres")

    def run() -> ExecutionResult:
        with engine.connect() as conn:
            if is_postgres:
                set_postgres_statement_timeout(conn, timeout_seconds)
            result = conn.execute(text(sql))
            columns = list(result.keys())
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
            return ExecutionResult(success=True, columns=columns, rows=rows)

    try:
        if is_postgres:
            return run()
        return run_with_timeout(run, timeout_seconds)
    except StatementTimeoutError as exc:
        return ExecutionResult(success=False, error=str(exc))
    except SQLAlchemyError as exc:
        return ExecutionResult(success=False, error=str(exc.orig) if exc.orig else str(exc))
