from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_ENV_FILE, extra="ignore")

    anthropic_api_key: str = ""
    groq_api_key: str = ""
    ollama_host: str = "http://localhost:11434"
    anthropic_model: str = "claude-sonnet-5"
    groq_model: str = "llama-3.3-70b-versatile"
    ollama_model: str = "llama3.1"

    model_provider: str = "anthropic"
    database_url: str = "sqlite:///./data/demo.db"

    statement_timeout_seconds: int = 10
    max_correction_attempts: int = 3
    default_row_limit: int = 200


def get_settings() -> Settings:
    return Settings()
