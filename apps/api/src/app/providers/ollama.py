import httpx

from app.providers.base import ModelProvider, ProviderError


class OllamaProvider(ModelProvider):
    name = "ollama"

    def __init__(self, host: str, model: str, timeout_seconds: float = 60.0):
        self.host = host.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    def generate(self, prompt: str) -> str:
        try:
            response = httpx.post(
                f"{self.host}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ProviderError(f"ollama request failed: {exc}") from exc

        data = response.json()
        return data.get("response", "")
