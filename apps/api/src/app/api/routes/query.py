from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.config import Settings, get_settings
from app.db.engine import get_engine
from app.pipeline.orchestrator import answer_question
from app.providers.factory import build_provider

router = APIRouter()


class QueryRequest(BaseModel):
    question: str


class AttemptResponse(BaseModel):
    sql: str
    success: bool
    error: str | None
    timestamp: str


class QueryResponse(BaseModel):
    sql: str
    success: bool
    columns: list[str] | None
    rows: list[dict] | None
    error: str | None
    attempts: list[AttemptResponse]
    model: str
    attempt_count: int
    latency_ms: int


@router.post("/query", response_model=QueryResponse)
def run_query(request: QueryRequest, settings: Settings = Depends(get_settings)) -> QueryResponse:
    engine = get_engine(settings.database_url)
    provider = build_provider(settings)

    result = answer_question(
        question=request.question,
        engine=engine,
        provider=provider,
        settings=settings,
    )

    return QueryResponse(
        sql=result.sql,
        success=result.success,
        columns=result.columns,
        rows=result.rows,
        error=result.error,
        attempts=[
            AttemptResponse(sql=a.sql, success=a.success, error=a.error, timestamp=a.timestamp)
            for a in result.attempts
        ],
        model=result.model,
        attempt_count=len(result.attempts),
        latency_ms=result.latency_ms,
    )
