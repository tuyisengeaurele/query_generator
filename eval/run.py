"""Runs the pipeline over a prepared BIRD subset and scores each answer with
execution accuracy. Writes one JSON results file per run.

Usage:
    python run.py --label with-correction --correction on
    python run.py --label no-correction --correction off
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent
REPO_ROOT = EVAL_DIR.parent
API_SRC = REPO_ROOT / "apps" / "api" / "src"
sys.path.insert(0, str(API_SRC))
sys.path.insert(0, str(REPO_ROOT))

from sqlalchemy import create_engine  # noqa: E402

from app.config import Settings  # noqa: E402
from app.pipeline.orchestrator import answer_question  # noqa: E402
from app.providers.factory import build_provider  # noqa: E402
from eval.scorer import execution_accuracy  # noqa: E402

SUBSET_PATH = EVAL_DIR / "data" / "subset" / "questions.json"
RESULTS_DIR = EVAL_DIR / "results"


def run_subset(label: str, correction_enabled: bool, limit: int | None) -> dict:
    questions = json.loads(SUBSET_PATH.read_text(encoding="utf-8"))
    if limit is not None:
        questions = questions[:limit]

    settings = Settings()
    provider = build_provider(settings)
    max_retries_override = None if correction_enabled else 0

    per_question = []
    correct = 0

    for item in questions:
        engine = create_engine(f"sqlite:///{item['db_path']}")
        started = time.perf_counter()
        try:
            result = answer_question(
                question=item["question"],
                engine=engine,
                provider=provider,
                settings=settings,
                max_retries_override=max_retries_override,
            )
            is_correct = result.success and execution_accuracy(engine, result.sql, item["gold_sql"])
            predicted_sql = result.sql
            attempt_count = len(result.attempts)
        except Exception as exc:  # a hard pipeline failure still counts as incorrect, not a crash
            is_correct = False
            predicted_sql = ""
            attempt_count = 0
            print(f"question {item['question_id']} raised {exc}", file=sys.stderr)

        elapsed_ms = int((time.perf_counter() - started) * 1000)
        correct += int(is_correct)
        per_question.append(
            {
                "question_id": item["question_id"],
                "db_id": item["db_id"],
                "question": item["question"],
                "gold_sql": item["gold_sql"],
                "predicted_sql": predicted_sql,
                "correct": is_correct,
                "attempt_count": attempt_count,
                "latency_ms": elapsed_ms,
            }
        )
        print(f"[{label}] {item['question_id']}: {'PASS' if is_correct else 'FAIL'}")

    accuracy = correct / len(questions) if questions else 0.0
    summary = {
        "label": label,
        "correction_enabled": correction_enabled,
        "total": len(questions),
        "correct": correct,
        "accuracy": accuracy,
        "questions": per_question,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RESULTS_DIR / f"run_{label}.json"
    output_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"[{label}] accuracy: {correct}/{len(questions)} = {accuracy:.1%}")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the pipeline over a BIRD subset")
    parser.add_argument("--label", required=True)
    parser.add_argument("--correction", choices=["on", "off"], required=True)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    run_subset(args.label, args.correction == "on", args.limit)


if __name__ == "__main__":
    main()
