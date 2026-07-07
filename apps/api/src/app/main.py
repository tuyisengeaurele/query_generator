from fastapi import FastAPI

from app.config import get_settings

app = FastAPI(title="Query Generator API", version="1.0.0")


@app.get("/health")
def health() -> dict:
    settings = get_settings()
    return {"status": "ok", "model_provider": settings.model_provider}
