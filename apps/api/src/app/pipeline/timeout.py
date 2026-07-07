from __future__ import annotations

import concurrent.futures
from typing import Any, Callable

from sqlalchemy import Connection, text


class StatementTimeoutError(RuntimeError):
    """Raised when a query runs longer than the configured statement
    timeout."""


def set_postgres_statement_timeout(conn: Connection, timeout_seconds: int) -> None:
    conn.execute(text(f"SET statement_timeout = {timeout_seconds * 1000}"))


def run_with_timeout(func: Callable[[], Any], timeout_seconds: int) -> Any:
    """SQLite has no native statement timeout, so this wraps the call in a
    worker thread and raises StatementTimeoutError if it does not finish in
    time. Used only for the SQLite path; Postgres uses SET statement_timeout
    instead since it can enforce the cutoff inside the database itself."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func)
        try:
            return future.result(timeout=timeout_seconds)
        except concurrent.futures.TimeoutError as exc:
            raise StatementTimeoutError(f"statement exceeded {timeout_seconds}s timeout") from exc
