from fastapi import FastAPI

from app.api.routes.query import router as query_router
from app.config import get_settings

app = FastAPI(title="Query Generator API", version="1.0.0")
app.include_router(query_router)


@app.get("/health")
def health() -> dict:
    settings = get_settings()
    return {"status": "ok", "model_provider": settings.model_provider}
