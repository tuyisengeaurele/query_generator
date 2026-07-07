# Query generator

Turns a plain English question into SQL, runs it safely against a real
database, and returns the result. The engineering work is the pipeline
around the model call: schema linking, few-shot retrieval, a SQL safety
guardrail, execution, and a self-correction loop driven by database
feedback. There is no fine-tuning anywhere in this project.

## Layout

```
apps/
  api/       FastAPI pipeline service (Python)
  web/       Demo app that queries a live database (React)
  landing/   Info site (React)
packages/
  design-tokens/   Shared color, type, spacing, motion tokens
  ui/              Shared React primitives used by web and landing
eval/        BIRD subset harness, execution-accuracy scorer, ablation report
data/        Demo schema, seed data, few-shot example pairs
docs/        Architecture notes
```

## Running the API

```
cd apps/api
python -m venv .venv
.venv/Scripts/pip install -e ".[dev]"
cp .env.example .env   # fill in ANTHROPIC_API_KEY or configure another provider
```

Build the local demo database once (SQLite stands in for Postgres in this
environment; see "Known limitations" below):

```
python data/build_sqlite_demo.py
```

Run the server from the repo root, so the default `DATABASE_URL` in `.env`
resolves against `data/demo.db`:

```
apps/api/.venv/Scripts/python -m uvicorn app.main:app --app-dir apps/api/src --port 8000
```

Endpoints: `GET /health`, `GET /schema`, `POST /query`.

Run the test suite:

```
cd apps/api
.venv/Scripts/pytest
```

## Running the demo web app

```
pnpm install
pnpm --filter web dev
```

Talks to the API through a dev-server proxy at `/api`. See
[apps/web/README.md](apps/web/README.md) for detail.

## Running the landing page

```
pnpm --filter landing dev
```

## Running the evaluation harness

```
cd eval
../apps/api/.venv/Scripts/python prepare_bird.py --limit 40
../apps/api/.venv/Scripts/python ablation.py --limit 40
```

Downloads the real BIRD dev set, slices a subset, and writes
`eval/results/ablation.md` comparing execution accuracy with the
self-correction loop on and off. See [eval/README.md](eval/README.md) for
detail, including current status.

## Model providers

One `ModelProvider` interface, three adapters: Ollama (local), Groq
(hosted, fast), Anthropic (hosted). Selected by the `MODEL_PROVIDER`
environment variable in `apps/api/.env`.

## Known limitations

- Postgres is the target database for the demo schema (`docker-compose.yml`,
  `data/demo_schema.sql`), but this repository was built in an environment
  without a local Docker install. The Postgres code path is implemented but
  not verified end to end here; the SQLite path (`data/build_sqlite_demo.py`)
  is what has actually been run and tested.
- The evaluation ablation report depends on live calls to the configured
  model provider. See [eval/README.md](eval/README.md) for the current
  status of that run.

## License

MIT. See [LICENSE](LICENSE).
