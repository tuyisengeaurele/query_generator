from abc import ABC, abstractmethod


class ModelProvider(ABC):
    """One method every provider adapter must implement: turn a prompt into
    raw model text. SQL extraction and validation happen downstream, not
    inside the adapter."""

    name: str

    @abstractmethod
    def generate(self, prompt: str) -> str:
        raise NotImplementedError


class ProviderError(RuntimeError):
    """Raised when a provider call fails, wrapping the underlying cause."""
