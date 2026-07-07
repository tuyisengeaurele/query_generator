"""Downloads the BIRD dev set and slices a configurable subset for local
evaluation runs. The full dev set is a few hundred SQLite databases and
around 1,500 questions; running the whole thing against a hosted model is
expensive, so this script writes a small, deterministic slice that the eval
runner then scores.

Usage:
    python prepare_bird.py --limit 250
"""

from __future__ import annotations

import argparse
import json
import urllib.request
import zipfile
from pathlib import Path

BIRD_DEV_URL = "https://bird-bench.oss-cn-beijing.aliyuncs.com/dev.zip"
EVAL_DIR = Path(__file__).resolve().parent
DATA_DIR = EVAL_DIR / "data"
ZIP_PATH = DATA_DIR / "dev.zip"
RAW_DIR = DATA_DIR / "raw"
SUBSET_DIR = DATA_DIR / "subset"


def download_dev_set() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if ZIP_PATH.exists():
        print(f"found existing archive at {ZIP_PATH}, skipping download")
        return
    print(f"downloading BIRD dev set from {BIRD_DEV_URL}")
    urllib.request.urlretrieve(BIRD_DEV_URL, ZIP_PATH)


def extract_dev_set() -> None:
    if RAW_DIR.exists() and any(RAW_DIR.iterdir()):
        print(f"found existing extracted data at {RAW_DIR}, skipping extraction")
        return
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print(f"extracting {ZIP_PATH} to {RAW_DIR}")
    with zipfile.ZipFile(ZIP_PATH) as archive:
        archive.extractall(RAW_DIR)


def _find_dev_json() -> Path:
    candidates = list(RAW_DIR.rglob("dev.json"))
    if not candidates:
        raise FileNotFoundError("dev.json not found inside the extracted BIRD archive")
    return candidates[0]


def _find_database_dir() -> Path:
    candidates = [p for p in RAW_DIR.rglob("dev_databases") if p.is_dir()]
    if not candidates:
        raise FileNotFoundError("dev_databases directory not found inside the extracted BIRD archive")
    return candidates[0]


def build_subset(limit: int) -> None:
    dev_json_path = _find_dev_json()
    database_dir = _find_database_dir()
    questions = json.loads(dev_json_path.read_text(encoding="utf-8"))

    sliced = []
    for item in questions:
        db_id = item["db_id"]
        db_path = database_dir / db_id / f"{db_id}.sqlite"
        if not db_path.exists():
            continue
        sliced.append(
            {
                "question_id": item.get("question_id"),
                "db_id": db_id,
                "question": item["question"],
                "evidence": item.get("evidence", ""),
                "gold_sql": item["SQL"],
                "difficulty": item.get("difficulty", "unknown"),
                "db_path": str(db_path),
            }
        )
        if len(sliced) >= limit:
            break

    SUBSET_DIR.mkdir(parents=True, exist_ok=True)
    output_path = SUBSET_DIR / "questions.json"
    output_path.write_text(json.dumps(sliced, indent=2), encoding="utf-8")
    print(f"wrote {len(sliced)} questions to {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a BIRD dev subset for evaluation")
    parser.add_argument("--limit", type=int, default=250, help="number of questions to slice (default 250)")
    parser.add_argument("--skip-download", action="store_true", help="assume dev.zip is already present")
    args = parser.parse_args()

    if not args.skip_download:
        download_dev_set()
    extract_dev_set()
    build_subset(args.limit)


if __name__ == "__main__":
    main()
