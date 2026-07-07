import httpx

from app.providers.base import ModelProvider, ProviderError

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


class GroqProvider(ModelProvider):
    name = "groq"

    def __init__(self, api_key: str, model: str, timeout_seconds: float = 30.0):
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds

    def generate(self, prompt: str) -> str:
        try:
            response = httpx.post(
                GROQ_API_URL,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0,
                },
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ProviderError(f"groq request failed: {exc}") from exc

        data = response.json()
        return data["choices"][0]["message"]["content"]
