# Natural language to SQL query generator implementation plan

> Execution note: given the size of this project (13 phases, three applications, a benchmark harness), this plan is executed inline, phase by phase, by the same engineer session that wrote it rather than dispatched to fresh subagents per micro-step. Each phase still ends in real commits, a pushed branch, and a PR merged into `develop`. Core pipeline logic (guardrails, schema linking, retrieval, executor, correction loop, scorer) gets real pytest coverage written before or alongside the implementation. Scaffolding, config, and markup files are written directly since they have no meaningful behavior to test.

**Goal:** Ship a working NL-to-SQL pipeline (API), a live demo web app, and a landing page, sharing one design system, with a real BIRD-subset benchmark and ablation report, released as `v1.0.0`.

**Architecture:** pnpm workspace monorepo (`apps/web`, `apps/landing`, `packages/design-tokens`, `packages/ui`) alongside a standalone Python project (`apps/api`, `eval/`). FastAPI serves the pipeline; SQLAlchemy is the database boundary (SQLite for BIRD and local dev standin, Postgres code path for the demo schema); React/Vite/Tailwind/shadcn power both frontends against shared tokens.

**Tech stack:** Python 3.11, FastAPI, SQLAlchemy, Pydantic Settings, pytest, sqlglot. Node 20+, pnpm workspaces, React 18, TypeScript, Vite, Tailwind, shadcn/ui, Framer Motion.

---

## Phase 0: Foundation

Files: `.gitignore`, `.editorconfig`, `LICENSE`, `pnpm-workspace.yaml`, `package.json`, `apps/api/pyproject.toml`, `.github/workflows/ci.yml`, `docker-compose.yml`, `.env.example` files.

- [x] `.gitignore` covering node_modules, `__pycache__`, `.venv`, `.env`, `dist`, `build`, eval data caches
- [x] `.editorconfig` (2-space JS/TS, 4-space Python, LF endings)
- [x] `LICENSE` (MIT, Ange Aurele Tuyisenge)
- [x] `pnpm-workspace.yaml` covering `apps/*` and `packages/*`
- [x] root `package.json` with workspace scripts
- [x] `apps/api/pyproject.toml` (FastAPI, SQLAlchemy, Pydantic, sqlglot, httpx, pytest deps)
- [x] `.github/workflows/ci.yml`: lint + test for Python and JS on push
- [x] `docker-compose.yml`: Postgres service + api service (documented, not locally exercised)
- [x] `.env.example` at repo root and `apps/api/.env.example`
- [x] commit, push, PR into develop, merge

## Phase 1: Design system

Files: `packages/design-tokens/src/*.ts`, `packages/design-tokens/css/tokens.css`, `packages/ui/src/*.tsx`, `docs/design-notes.md`.

- [x] token definitions (color, type, spacing, motion) as TS consts and CSS custom properties
- [x] shared primitives: Button, Badge, Card, CodeBlock (mono), Panel
- [x] design notes doc explaining the warm/cool duality rule
- [x] commit, push, PR, merge

## Phase 2: API foundation

Files: `apps/api/src/app/main.py`, `apps/api/src/app/config.py`, `apps/api/src/app/db/engine.py`, `apps/api/src/app/db/introspect.py`, `apps/api/tests/test_introspect.py`.

- [x] FastAPI app + `/health`
- [x] Pydantic Settings reading `.env` (`ANTHROPIC_API_KEY`, `DATABASE_URL`, `MODEL_PROVIDER`)
- [x] SQLAlchemy engine factory for sqlite:// and postgresql:// URLs
- [x] schema introspection (tables, columns, types, PK, FK, sample values), with an in-process cache keyed by engine URL
- [x] pytest covering introspection against a throwaway SQLite fixture DB
- [x] commit, push, PR, merge

## Phase 3: Model adapters

Files: `apps/api/src/app/providers/base.py`, `ollama.py`, `groq.py`, `anthropic.py`, `apps/api/tests/test_providers.py`.

- [x] `ModelProvider` ABC: `generate(prompt: str) -> str`
- [x] Ollama adapter (local HTTP), Groq adapter, Anthropic adapter (`anthropic` SDK, model configurable, key from settings)
- [x] provider factory keyed by `MODEL_PROVIDER` env var
- [x] tests using a fake/mocked provider plus adapter construction tests (no live network calls in CI)
- [x] commit, push, PR, merge

## Phase 4: Pipeline core

Files: `apps/api/src/app/pipeline/schema_linking.py`, `few_shot.py`, `prompt.py`, `sql_extract.py`, `data/examples/*.json`, tests.

- [x] `SchemaLinker` interface + `FullSchemaLinker`
- [x] few-shot example store loaded from `data/examples/pairs.json`, naive embedding-free keyword retriever as the MVP (swappable)
- [x] prompt builder combining linked schema + examples + question, natural language left as-is, schema/SQL fenced
- [x] SQL extraction: strip code fences/prose from a raw model response, normalize whitespace
- [x] tests for extraction edge cases (fenced, unfenced, trailing prose, multiple fences)
- [x] commit, push, PR, merge

## Phase 5: Safety guardrails

Files: `apps/api/src/app/pipeline/guardrails.py`, tests.

- [x] parse with `sqlglot`, reject non-single-SELECT statements
- [x] reject DDL/DML keywords anywhere in the parsed tree, not just top-level
- [x] strip comments before parsing, do not rely on regex alone
- [x] inject `LIMIT 200` when absent
- [x] statement timeout wrapper (SQLAlchemy `execution_options` for Postgres, thread-based timeout for SQLite)
- [x] tests: valid SELECT passes, INSERT/UPDATE/DELETE/DROP/ATTACH rejected, multi-statement rejected, comment-smuggled statement rejected, limit injected when missing, existing limit left alone
- [x] commit, push, PR, merge

## Phase 6: Execution and correction loop

Files: `apps/api/src/app/pipeline/executor.py`, `correction.py`, `orchestrator.py`, `apps/api/src/app/api/routes/query.py`, tests.

- [x] executor: runs guarded SQL, returns rows or the raw DB error string
- [x] correction loop: on DB error or an empty-result-when-rows-implied heuristic, re-prompt with error + question + schema, cap 3 retries, record every attempt (sql, error, timestamp)
- [x] orchestrator wires stages 1-9 end to end, returns final SQL, trace, rows, model, attempts, latency_ms
- [x] `POST /query` endpoint, request/response Pydantic models
- [x] tests: loop stops on first success, loop exhausts at 3 and returns last attempt with trace, trace records every attempt
- [x] commit, push, PR, merge

## Phase 7: Advanced schema linking

Files: `apps/api/src/app/pipeline/embeddings.py`, `embedding_linker.py`, tests.

- [x] embedding backend (local sentence-transformers-style or provider-based embedding call, behind its own small interface)
- [x] `EmbeddingSchemaLinker` implementing the same `SchemaLinker` interface, top-k tables/columns by cosine similarity
- [x] selection logic: use `EmbeddingSchemaLinker` above a configurable table/column count threshold, `FullSchemaLinker` below it
- [x] tests with fixed fake embeddings (deterministic, no live network calls)
- [x] commit, push, PR, merge

## Phase 8: Evaluation

Files: `eval/prepare_bird.py`, `eval/scorer.py`, `eval/run.py`, `eval/ablation.py`, `eval/results/ablation.md`, `eval/README.md`.

- [x] `prepare_bird.py`: downloads BIRD dev set, slices a configurable subset (default 250, local run uses 40), writes SQLite DBs + questions/gold SQL to `eval/data/`
- [x] `scorer.py`: execution accuracy, unordered row-set comparison
- [x] `run.py`: runs the pipeline over the subset with a given correction-loop setting, writes per-question results
- [x] `ablation.py`: runs `run.py` twice (correction off, correction on), builds `eval/results/ablation.md` with both scores and the point difference, notes the false-negative limitation of strict execution accuracy
- [x] commit, push, PR, merge (report content depends on an actual run against the 40-question slice with the Anthropic key)

## Phase 9: Demo web app

Files: `apps/web/*` (Vite/React/Tailwind scaffold), `src/components/QueryConsole.tsx`, `SqlView.tsx`, `ResultGrid.tsx`, `SchemaBrowser.tsx`, `CorrectionTrace.tsx`, `StarterChips.tsx`, `data/demo_schema.sql`, `data/demo_seed.sql`, component tests.

- [x] Vite scaffold, Tailwind config pulling `packages/design-tokens`, shadcn/ui setup
- [x] demo schema + seed data (`cooperatives`, `members`, `products`, `orders`, `order_items`, `payments`), SQLite file used locally as the Postgres standin, loaded through the same API
- [x] query console (question input, starter chips, submit) calling `POST /query`
- [x] SQL view with syntax highlighting, correction trace (collapsed/expandable), result grid, latency, model badge
- [x] schema browser panel driven by `/schema`
- [x] component tests for QueryConsole, ResultGrid, CorrectionTrace
- [x] commit, push, PR, merge

## Phase 10: Landing page

Files: `apps/landing/*`, `src/sections/Hero.tsx`, `HowItWorks.tsx`, `Pipeline.tsx`, `Benchmark.tsx`, `Architecture.tsx`, `Footer.tsx`.

- [x] Vite scaffold sharing tokens/UI package
- [x] hero translation sequence (Framer Motion, respects `prefers-reduced-motion`)
- [x] how-it-works, pipeline stages, benchmark (pulls the real ablation numbers), architecture sections
- [x] footer with no repository or social links
- [x] responsive pass, motion polish
- [x] commit, push, PR, merge

## Phase 11: Hardening and docs

Files: `apps/api/src/app/logging.py`, error handlers, root `README.md`, `docs/architecture.md`, `apps/api/tests/test_integration.py`, CI coverage config.

- [x] structured logging + latency metrics on `/query`
- [x] error handling for provider failures, DB connection failures, guardrail rejections (clean 4xx/5xx, no stack traces leaked)
- [x] root README (setup, running each app, running eval), `docs/architecture.md`
- [x] one integration test exercising `/query` end to end against a seeded SQLite DB
- [x] CI runs coverage
- [x] commit, push, PR, merge

## Phase 12: Release

- [x] release PR: `develop` -> `main`
- [x] merge with `--no-ff`
- [x] tag `v1.0.0` on `main`
- [x] push tag
