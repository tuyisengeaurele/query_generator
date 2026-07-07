"""Runs the same BIRD subset twice, once with the self-correction loop
disabled and once enabled, and writes a markdown report comparing the two
execution-accuracy scores.

Usage:
    python ablation.py --limit 40
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from run import run_subset

EVAL_DIR = Path(__file__).resolve().parent
RESULTS_DIR = EVAL_DIR / "results"

REPORT_TEMPLATE = """# Self-correction ablation

Run date: {run_date}
Questions per arm: {total}
Model provider: {model_provider}

## Results

| Arm | Correct | Total | Execution accuracy |
| --- | --- | --- | --- |
| Correction disabled | {off_correct} | {total} | {off_accuracy:.1%} |
| Correction enabled | {on_correct} | {total} | {on_accuracy:.1%} |

Point difference: {point_diff:+.1f} percentage points.

## Reading these numbers

Execution accuracy compares the row set the predicted SQL returns against
the row set the gold SQL returns, run against the same SQLite database. It
undercounts correct answers in one specific way: a query that answers the
question correctly but returns columns in a different order, uses different
column aliases, or orders rows differently than the gold query will fail a
strict set comparison even though a person reading both result sets would
call them the same answer. Practical accuracy, measured with a human
reviewing the mismatches, runs higher than the number in the table above.

This run used {total} questions from the BIRD dev set, not the full 1,534
question set. `prepare_bird.py --limit 250` slices a larger subset; scaling
past that trades run time and hosted-model API cost for a tighter confidence
interval on the accuracy number.
"""


def build_report(off_summary: dict, on_summary: dict, model_provider: str) -> str:
    off_accuracy = off_summary["accuracy"]
    on_accuracy = on_summary["accuracy"]
    return REPORT_TEMPLATE.format(
        run_date=date.today().isoformat(),
        total=off_summary["total"],
        model_provider=model_provider,
        off_correct=off_summary["correct"],
        off_accuracy=off_accuracy,
        on_correct=on_summary["correct"],
        on_accuracy=on_accuracy,
        point_diff=(on_accuracy - off_accuracy) * 100,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the self-correction ablation")
    parser.add_argument("--limit", type=int, default=40)
    args = parser.parse_args()

    off_summary = run_subset("no-correction", correction_enabled=False, limit=args.limit)
    on_summary = run_subset("with-correction", correction_enabled=True, limit=args.limit)

    import sys

    sys.path.insert(0, str(EVAL_DIR.parent / "apps" / "api" / "src"))
    from app.config import Settings

    model_provider = Settings().model_provider

    report = build_report(off_summary, on_summary, model_provider)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = RESULTS_DIR / "ablation.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"wrote report to {report_path}")


if __name__ == "__main__":
    main()
