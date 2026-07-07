from __future__ import annotations

import sqlglot
from sqlglot import exp

FORBIDDEN_EXPRESSIONS = (
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Drop,
    exp.Alter,
    exp.Create,
    exp.TruncateTable,
    exp.Grant,
    exp.Attach,
    exp.Command,
)


class GuardrailViolation(ValueError):
    """Raised when a generated statement fails a safety check. The message
    is safe to show to a caller since it never echoes raw exception
    internals from the SQL engine."""


def enforce_guardrails(sql: str, dialect: str, default_limit: int) -> str:
    """Validates that sql is exactly one read-only SELECT statement, then
    returns it with a LIMIT injected if it did not already have one.
    Raises GuardrailViolation for anything else."""
    stripped = sql.strip()
    if not stripped:
        raise GuardrailViolation("empty SQL is not allowed")

    try:
        statements = sqlglot.parse(stripped, read=dialect)
    except Exception as exc:
        raise GuardrailViolation(f"could not parse SQL: {exc}") from exc

    statements = [s for s in statements if s is not None]
    if len(statements) != 1:
        raise GuardrailViolation("only a single SQL statement is allowed")

    statement = statements[0]

    if not isinstance(statement, exp.Select):
        raise GuardrailViolation("only SELECT statements are allowed")

    for forbidden in FORBIDDEN_EXPRESSIONS:
        if list(statement.find_all(forbidden)):
            raise GuardrailViolation(f"statement contains a forbidden operation: {forbidden.__name__}")

    if statement.args.get("limit") is None:
        statement = statement.limit(default_limit)

    return statement.sql(dialect=dialect)
