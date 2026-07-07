# Evaluation harness

Scores the pipeline against a subset of the BIRD dev set using execution
accuracy: run the predicted SQL and the gold SQL against the same SQLite
database, compare the result sets.

## Setup

Uses the same Python environment as `apps/api` (the harness imports the
pipeline directly rather than going through HTTP). From the repo root:

```
cd apps/api
python -m venv .venv
.venv/Scripts/pip install -e ".[dev]"
```

Set `ANTHROPIC_API_KEY` (or configure a different `MODEL_PROVIDER`) in
`apps/api/.env` before running, since scoring calls the live model for
every question.

## Preparing data

```
cd eval
../apps/api/.venv/Scripts/python prepare_bird.py --limit 250
```

Downloads the BIRD dev set (about 350MB) on first run, extracts it, and
writes a `data/subset/questions.json` slice of the requested size. Rerunning
with `--skip-download` reuses the already-extracted archive.

## Running the ablation

```
../apps/api/.venv/Scripts/python ablation.py --limit 40
```

Runs the prepared subset twice, once with the self-correction loop disabled
and once enabled, and writes `results/ablation.md` with both execution
accuracy numbers and the point difference between them. The default local
run in this repository used a 40-question slice to keep API cost and run
time reasonable; the harness itself has no limit beyond what `prepare_bird.py`
sliced, so a full 250-question run only requires re-running `prepare_bird.py`
with a larger `--limit` first.

## Running one arm at a time

```
../apps/api/.venv/Scripts/python run.py --label with-correction --correction on --limit 40
../apps/api/.venv/Scripts/python run.py --label no-correction --correction off --limit 40
```

Each run writes `results/run_<label>.json` with per-question detail:
predicted SQL, gold SQL, whether it scored correct, attempt count, and
latency.
