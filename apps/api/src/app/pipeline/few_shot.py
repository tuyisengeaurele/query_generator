from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

DEFAULT_EXAMPLES_PATH = Path(__file__).resolve().parents[5] / "data" / "examples" / "pairs.json"

_STOPWORDS = {"the", "a", "an", "of", "for", "to", "in", "on", "is", "are", "how", "many", "what", "which"}


@dataclass
class ExamplePair:
    question: str
    sql: str


def load_examples(path: Path = DEFAULT_EXAMPLES_PATH) -> list[ExamplePair]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [ExamplePair(question=item["question"], sql=item["sql"]) for item in raw]


def _keywords(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {w for w in words if w not in _STOPWORDS}


class FewShotRetriever:
    """Ranks stored example pairs by keyword overlap with the question. A
    lightweight, dependency-free stand-in for an embedding retriever; swap
    for a vector search once the example library grows past a few dozen
    pairs."""

    def __init__(self, examples: list[ExamplePair]):
        self.examples = examples

    def retrieve(self, question: str, top_k: int = 3) -> list[ExamplePair]:
        question_words = _keywords(question)
        if not question_words:
            return self.examples[:top_k]

        scored = []
        for example in self.examples:
            overlap = len(question_words & _keywords(example.question))
            scored.append((overlap, example))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [example for _, example in scored[:top_k]]
