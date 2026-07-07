from app.config import Settings
from app.providers.anthropic_provider import AnthropicProvider
from app.providers.base import ModelProvider
from app.providers.groq import GroqProvider
from app.providers.ollama import OllamaProvider


def build_provider(settings: Settings) -> ModelProvider:
    provider = settings.model_provider.lower()

    if provider == "anthropic":
        return AnthropicProvider(api_key=settings.anthropic_api_key, model=settings.anthropic_model)
    if provider == "groq":
        return GroqProvider(api_key=settings.groq_api_key, model=settings.groq_model)
    if provider == "ollama":
        return OllamaProvider(host=settings.ollama_host, model=settings.ollama_model)

    raise ValueError(f"unknown model provider: {settings.model_provider}")
