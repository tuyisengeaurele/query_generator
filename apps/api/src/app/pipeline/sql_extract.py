import re

_FENCE_PATTERN = re.compile(r"```(?:sql)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def extract_sql(raw_response: str) -> str:
    """Pulls clean SQL out of a raw model response. Prefers the first fenced
    code block; falls back to the raw text with prose lines stripped when
    no fence is present."""
    match = _FENCE_PATTERN.search(raw_response)
    if match:
        candidate = match.group(1)
    else:
        candidate = raw_response

    return _normalize(candidate)


def _normalize(sql: str) -> str:
    lines = [line.strip() for line in sql.strip().splitlines()]
    lines = [line for line in lines if line and not line.startswith("--")]
    normalized = " ".join(lines)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized.rstrip(";")
