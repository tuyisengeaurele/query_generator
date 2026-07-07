from __future__ import annotations

import hashlib
import re
from abc import ABC, abstractmethod

import numpy as np

EMBEDDING_DIM = 256


class Embedder(ABC):
    @abstractmethod
    def embed(self, text: str) -> np.ndarray:
        raise NotImplementedError


class HashingEmbedder(Embedder):
    """Deterministic, dependency-free embedder: each token is hashed into a
    fixed-size vector (the feature hashing trick). No network call, no
    randomness, so it is safe to unit test and to run without any API key.
    Swap for a real embedding provider by implementing the Embedder
    interface; EmbeddingSchemaLinker does not care which one it gets."""

    def embed(self, text: str) -> np.ndarray:
        vector = np.zeros(EMBEDDING_DIM, dtype=np.float64)
        tokens = re.findall(r"[a-z0-9]+", text.lower())
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % EMBEDDING_DIM
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign
        norm = np.linalg.norm(vector)
        return vector / norm if norm > 0 else vector


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)
