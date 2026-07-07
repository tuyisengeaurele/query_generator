from __future__ import annotations

import time
from dataclasses import dataclass

from sqlalchemy import Engine

from app.config import Settings
from app.db.introspect import introspect_schema
from app.pipeline.correction import Attempt, run_with_correction
from app.pipeline.few_shot import DEFAULT_EXAMPLES_PATH, FewShotRetriever, load_examples
from app.pipeline.prompt import build_prompt
from app.pipeline.schema_linking import FullSchemaLinker, SchemaLinker
from app.pipeline.sql_extract import extract_sql
from app.providers.base import ModelProvider

EMBEDDING_LINKER_TABLE_THRESHOLD = 12


@dataclass
class QueryResult:
    sql: str
    success: bool
    columns: list[str] | None
    rows: list[dict] | None
    error: str | None
    attempts: list[Attempt]
    model: str
    latency_ms: int


def _dialect_for(engine: Engine) -> str:
    backend = engine.url.get_backend_name()
    return "postgres" if backend.startswith("postgres") else "sqlite"


def select_linker(table_count: int) -> SchemaLinker:
    if table_count > EMBEDDING_LINKER_TABLE_THRESHOLD:
        from app.pipeline.embedding_linker import EmbeddingSchemaLinker

        return EmbeddingSchemaLinker()
    return FullSchemaLinker()


def answer_question(
    *,
    question: str,
    engine: Engine,
    provider: ModelProvider,
    settings: Settings,
    max_retries_override: int | None = None,
) -> QueryResult:
    started_at = time.perf_counter()

    db_schema = introspect_schema(engine)
    linker = select_linker(len(db_schema.tables))
    linked_schema = linker.link(question, db_schema)

    examples = load_examples(DEFAULT_EXAMPLES_PATH) if DEFAULT_EXAMPLES_PATH.exists() else []
    retrieved_examples = FewShotRetriever(examples).retrieve(question) if examples else []

    def generate_initial_sql() -> str:
        prompt = build_prompt(question, linked_schema, retrieved_examples)
        return extract_sql(provider.generate(prompt))

    dialect = _dialect_for(engine)
    final_sql, result, attempts = run_with_correction(
        question=question,
        schema=linked_schema,
        provider=provider,
        generate_initial_sql=generate_initial_sql,
        engine=engine,
        dialect=dialect,
        default_limit=settings.default_row_limit,
        timeout_seconds=settings.statement_timeout_seconds,
        max_retries=max_retries_override if max_retries_override is not None else settings.max_correction_attempts,
    )

    latency_ms = int((time.perf_counter() - started_at) * 1000)

    return QueryResult(
        sql=final_sql,
        success=result.success,
        columns=result.columns,
        rows=result.rows,
        error=result.error,
        attempts=attempts,
        model=provider.name,
        latency_ms=latency_ms,
    )
