import time

from fastapi import FastAPI, Request

from app.api.routes.query import router as query_router
from app.api.routes.schema import router as schema_router
from app.config import get_settings
from app.errors import register_error_handlers
from app.logging_config import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)

app = FastAPI(title="Query Generator API", version="1.0.0")
app.include_router(query_router)
app.include_router(schema_router)
register_error_handlers(app)


@app.middleware("http")
async def log_request_latency(request: Request, call_next):
    started_at = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = int((time.perf_counter() - started_at) * 1000)
    logger.info("%s %s -> %s in %dms", request.method, request.url.path, response.status_code, elapsed_ms)
    return response


@app.get("/health")
def health() -> dict:
    settings = get_settings()
    return {"status": "ok", "model_provider": settings.model_provider}
