import anthropic

from app.providers.base import ModelProvider, ProviderError


class AnthropicProvider(ModelProvider):
    name = "anthropic"

    def __init__(self, api_key: str, model: str, max_tokens: int = 1024):
        self.model = model
        self.max_tokens = max_tokens
        self._client = anthropic.Anthropic(api_key=api_key)

    def generate(self, prompt: str) -> str:
        try:
            message = self._client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
        except anthropic.APIError as exc:
            raise ProviderError(f"anthropic request failed: {exc}") from exc

        return "".join(block.text for block in message.content if block.type == "text")
