from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.logging_config import get_logger
from app.pipeline.guardrails import GuardrailViolation
from app.providers.base import ProviderError

logger = get_logger(__name__)


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(GuardrailViolation)
    async def handle_guardrail_violation(request: Request, exc: GuardrailViolation) -> JSONResponse:
        logger.warning("guardrail rejected a request: %s", exc)
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(ProviderError)
    async def handle_provider_error(request: Request, exc: ProviderError) -> JSONResponse:
        logger.error("model provider call failed: %s", exc)
        return JSONResponse(status_code=502, content={"detail": "the model provider request failed"})

    @app.exception_handler(SQLAlchemyError)
    async def handle_database_error(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        logger.error("database error: %s", exc)
        return JSONResponse(status_code=503, content={"detail": "the database is unavailable"})

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled error while processing %s", request.url.path)
        return JSONResponse(status_code=500, content={"detail": "an unexpected error occurred"})
