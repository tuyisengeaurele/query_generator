# Natural language to SQL query generator, design spec

Date: 2026-07-08

## Problem

A person asks a question in plain English. The system must produce SQL that answers it, run that SQL safely against a real database, and return a result set the person can trust. This is a pipeline problem, not a single model call: the model needs the right schema context, needs examples of the house style for SQL, needs guardrails that keep it from ever running anything destructive, and needs a way to recover when its first attempt does not execute.

The project has three surfaces that share one visual identity: a Python pipeline API, a demo web app querying a live database, and a landing page that explains the product. There is no fine-tuning anywhere in this project.

## Architecture

Monorepo, pnpm workspaces for JS, standard Python project for the API and eval.

```
query_generator/
  apps/
    api/            FastAPI pipeline service
    web/             React demo app (Vite, Tailwind, shadcn/ui)
    landing/          React info site (Vite, Tailwind)
  packages/
    design-tokens/    Shared color, type, spacing, motion tokens (TS + CSS vars)
    ui/               Shared React components used by web and landing
  eval/               BIRD harness, scorer, ablation report
  data/               Demo schema SQL, seed data, example question and SQL pairs
  docs/               Architecture and design notes
  .github/workflows/  CI: lint and test on push
```

### Pipeline stages (apps/api)

1. **Schema introspection.** SQLAlchemy reflects tables, columns, types, primary keys, foreign keys, and a handful of sample values per column. Cached per connection.
2. **Schema linking.** A `SchemaLinker` interface with two implementations: `FullSchemaLinker` (passes everything, used when the schema is small) and `EmbeddingSchemaLinker` (ranks tables and columns by embedding similarity to the question, used for larger schemas). Swappable behind the interface, selected by schema size or config.
3. **Few-shot retrieval.** A stored library of question and SQL pairs in `data/examples`. A retriever embeds the question and pulls the closest matches for the prompt.
4. **Prompt assembly.** Builds the model prompt from linked schema, retrieved examples, and the question. Natural language stays as-is; schema and SQL are always formatted in fenced code blocks.
5. **Generation.** Provider adapter call, then SQL extraction (strip fences and prose, normalize whitespace).
6. **Guardrails.** Parses the SQL with `sqlglot`. Rejects anything that is not exactly one read-only `SELECT` statement. Rejects DDL, DML, multiple statements, and comment-based smuggling. Injects a `LIMIT` when none is present. Enforces a statement timeout. Executes through a database role with read-only grants (Postgres) or a read-only connection mode (SQLite).
7. **Execution.** Runs the SQL, returns rows or the database error text.
8. **Self-correction loop.** On a database error, or an empty result where the question implies rows should exist, feeds the error, question, and schema back to the model. Capped at three retries. Every attempt (SQL, error if any, timestamp) is recorded in the trace.
9. **Response.** Final SQL, full attempt trace, result rows, model name, attempt count, and latency in milliseconds.

### Model providers

One `ModelProvider` interface (`generate(prompt) -> str`), three adapters: `OllamaProvider`, `GroqProvider`, `AnthropicProvider`. Selected by `MODEL_PROVIDER` env var. The demo defaults to Anthropic (key supplied and stored in `apps/api/.env`, gitignored). The eval runner defaults to whatever `MODEL_PROVIDER` is configured; local runs with Ollama need no paid key.

### Database support

SQLAlchemy engine abstraction supporting SQLite and Postgres. BIRD databases are SQLite. The demo schema is written for Postgres via `docker-compose.yml`, but this environment has no Docker installed, so local verification of the demo runs against SQLite with the same schema and seed data translated to SQLite-compatible DDL. The Postgres path (engine URL handling, read-only role SQL, docker-compose service) is implemented and documented, not verified end-to-end in this environment. This limitation is stated plainly in the demo README, not glossed over.

## Evaluation

`eval/` prepares a configurable subset of the BIRD dev set (default 250 questions, downloaded from the real BIRD source) and the matching SQLite databases. Execution accuracy scoring: run generated SQL and gold SQL, compare result sets as unordered row sets. The ablation runs the same subset twice, once with self-correction disabled and once enabled, and writes `eval/results/ablation.md` with both numbers, the point difference, and a note that strict execution accuracy produces false negatives (a query that returns a correct but differently-ordered or differently-aliased result set can still fail a naive comparison), so practical accuracy with a human review step runs higher.

Given the cost of calling a live hosted model (250 questions times up to 3 retries times 2 ablation arms is potentially over a thousand calls), the local run executed as part of this build uses a 40-question slice by default. The harness itself supports the full 250-question default via config, documented in `eval/README.md` for the user to run later at their own pace and cost.

## Guardrail detail

- SQL parsed with `sqlglot`, target dialect matches the connection.
- Reject if parse produces more than one statement, or the single statement's root is not `SELECT`.
- Reject on keywords for DDL/DML (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, `TRUNCATE`, `GRANT`, `ATTACH`) appearing anywhere in the parsed statement, not just the root, since a smuggled statement inside a CTE or subquery must also be caught.
- Strip SQL comments before parsing so a comment cannot hide a second statement from a naive string check; the parser is the source of truth, not a regex.
- If no `LIMIT` clause exists, append `LIMIT 200`.
- Statement timeout: `SET statement_timeout` for Postgres, a wrapper-level timer for SQLite (SQLite has no native statement timeout).
- Execution always goes through a connection whose grants are read-only (Postgres role) or whose Python-level access is restricted to `SELECT` (SQLite has no roles, so the guardrail layer is the only enforcement there, which is why the parse-level rejection matters most for SQLite).

## Demo web app (apps/web)

React 18, TypeScript, Vite, Tailwind, shadcn/ui, Framer Motion, a SQL syntax highlighter. Seeded schema: cooperative sales domain (`cooperatives`, `members`, `products`, `orders`, `order_items`, `payments`). UI: question input with starter chips, generated SQL panel with highlighting, correction trace (collapsed by default, expandable), result grid, latency readout, model badge. Everything read-only.

## Landing page (apps/landing)

React 18, TypeScript, Vite, Tailwind. Explains the problem, the pipeline stage by stage, the benchmark result with the same honest framing as the eval report, and the architecture. No links to any code repository, no "star on GitHub," no social links. Hero section: an orchestrated sequence showing a typed question in Fraunces resolving into linked schema, then mono SQL, then a result grid. Respects `prefers-reduced-motion`.

## Design system (packages/design-tokens, packages/ui)

Palette (fixed, no purple/violet/indigo anywhere): `ink #0C0E10`, `surface #15181B`, `raised #1D2125`, `hairline #2A2F34`, `text #ECEBE7`, `muted #8A9199`, `signal-warm #E8A13C`, `signal-cool #57C7B4`, `ok #5FB878`, `err #E0575B`. Type: Fraunces (display/serif, natural language), Geist Sans with Inter fallback (body/UI), JetBrains Mono (SQL, schema, data, always). Motion: Framer Motion, one orchestrated hero sequence, subtle staggered scroll reveals (~20px translate and fade), custom easing, `prefers-reduced-motion` respected, no infinite background loops.

## Git and process decisions (superseding the original 50-plus-PR ask)

- Branches: `main` (release), `develop` (integration), short-lived `feat/`, `fix/`, `chore/`, `test/`, `docs/`, `ci/` branches off `develop`.
- Roughly 19 pull requests covering the 13 phases below, each with 2 or more Conventional Commits, pushed, opened with `gh pr create` into `develop`, merged with `gh pr merge --no-ff`, branch deleted after merge.
- Periodic `develop` to `main` release PRs, final one tags `v1.0.0`.
- This replaces the "50-plus feature branches, 100-plus commits" instruction from the original brief. The user approved this trade-off directly: fewer, larger PRs over a mechanically inflated branch count. Commit count and PR count will land well under the original numeric targets; phase coverage and the definition of done otherwise hold.

Phase to PR mapping:

0. Foundation - 1 PR: init, gitignore, editorconfig, license, pnpm workspace, Python project config, CI skeleton, docker-compose.
1. Design system - 2 PRs: tokens; shared UI primitives plus design notes doc.
2. API foundation - 2 PRs: FastAPI scaffold, settings, health endpoint; SQLAlchemy adapter, schema introspection, adapter tests.
3. Model adapters - 2 PRs: provider interface, Ollama adapter, Groq adapter; Anthropic adapter, mocked-provider tests.
4. Pipeline core - 2 PRs: prompt builder, full-schema linker; few-shot retrieval, SQL extraction and normalization, tests.
5. Safety - 1 PR: statement guardrail, limit injection, timeout, read-only role wiring, tests.
6. Execution and correction - 2 PRs: executor, self-correction loop; orchestrator, `/query` endpoint, loop tests.
7. Advanced schema linking - 1 PR: schema embeddings, top-k retriever, tests.
8. Evaluation - 2 PRs: BIRD subset loader, execution-accuracy scorer; eval runner, ablation report.
9. Demo web app - 3 PRs: scaffold and theme wiring; query console, SQL view, result grid; schema browser, correction trace view, starter chips, component tests.
10. Landing page - 2 PRs: scaffold and hero sequence; remaining sections, motion polish, responsive pass.
11. Hardening and docs - 1 PR: logging and latency metrics, error handling, README, architecture doc, env examples, integration test, CI coverage.
12. Release - 1 PR: release prep, `develop` merged to `main`, tag `v1.0.0`.

## Writing rules (applies to README, all docs, all code comments, all UI copy)

No em dashes anywhere, in any file, in any surface. No AI tell words (delve, leverage, seamless, robust, elevate, unlock, dive in, harness, realm, landscape, tapestry, testament, showcase, boasts, ever-evolving, "in today's world," "it is worth noting," "at the end of the day"). Active voice. Specific numbers and names instead of vague claims. No throat-clearing openers. Sentence case for headings and buttons. This rule applies to code comments and in-app content, not just markdown docs.

## Testing

pytest for the API: unit tests per pipeline stage (introspection, linking, retrieval, guardrails, executor, correction loop), one integration test exercising `/query` end to end against a seeded SQLite database. Component tests for the web app (query console, result grid, trace view). CI runs lint and test on every push.

## Known limitations (stated honestly in docs, not hidden)

- Postgres path is implemented but not verified against a real Postgres instance in this environment (no Docker available). SQLite stands in for local verification.
- Local eval run in this build uses a 40-question BIRD slice, not the full 250, for time and API cost reasons. The harness supports 250 via config.
- PR and commit counts are lower than the original 50-plus-PR, 100-plus-commit target, by explicit user approval.
