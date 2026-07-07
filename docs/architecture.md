# Architecture

## Pipeline stages

A question enters through `POST /query` and moves through nine stages,
implemented in `apps/api/src/app/pipeline`:

1. **Schema introspection** (`db/introspect.py`). SQLAlchemy reflects
   tables, columns, types, primary keys, foreign keys, and up to three
   sample values per column. Cached per engine URL in process memory.
2. **Schema linking** (`pipeline/schema_linking.py`,
   `pipeline/embedding_linker.py`). `SchemaLinker` is an interface with two
   implementations: `FullSchemaLinker` passes every table through
   unfiltered, and `EmbeddingSchemaLinker` ranks tables by similarity to the
   question and keeps the top few plus anything reachable by a foreign key.
   The orchestrator picks the embedding linker once a database has more
   than 12 tables.
3. **Few-shot retrieval** (`pipeline/few_shot.py`). A stored library of
   question and SQL pairs (`data/examples/pairs.json`) ranked by keyword
   overlap with the question.
4. **Prompt assembly** (`pipeline/prompt.py`). Combines the linked schema,
   retrieved examples, and the question into one prompt. A second template,
   `build_correction_prompt`, adds the failed SQL and the database error for
   retry attempts.
5. **Generation** (`providers/`). One `ModelProvider` interface, three
   adapters (Ollama, Groq, Anthropic) selected by the `MODEL_PROVIDER`
   environment variable.
6. **SQL extraction** (`pipeline/sql_extract.py`). Pulls SQL out of the raw
   model response: prefers a fenced code block, strips comments and prose,
   normalizes whitespace.
7. **Guardrails** (`pipeline/guardrails.py`). Parses the SQL with `sqlglot`
   and rejects anything that is not exactly one `SELECT` statement,
   including DDL or DML hidden inside a CTE and comment-smuggled second
   statements. Injects a default `LIMIT` when the model omits one.
8. **Execution** (`pipeline/executor.py`). Runs the guarded SQL. SQLite gets
   a thread-based timeout wrapper (`pipeline/timeout.py`) since it has no
   native statement timeout; Postgres uses `SET statement_timeout` on the
   connection. Returns rows and columns on success, or the raw database
   error text on failure.
9. **Self-correction** (`pipeline/correction.py`). On a database error, or
   an empty result where the question phrasing implies rows should exist
   (`looks_like_rows_were_expected`), re-prompts the model with the error
   attached and tries again. Capped at three retries beyond the first
   attempt (four attempts total). Every attempt is recorded with its SQL,
   success flag, error, and timestamp.

`pipeline/orchestrator.py` wires all nine stages together and returns the
final SQL, the full attempt trace, result rows, the provider name, attempt
count, and end-to-end latency in milliseconds.

## Safety

Two independent layers stop a write from ever happening:

- The guardrail parser (`pipeline/guardrails.py`) rejects any statement that
  is not a single read-only `SELECT`, checked at the AST level so a
  forbidden operation hidden inside a subquery or CTE is still caught.
- The database connection itself carries read-only grants. For Postgres,
  `data/demo_readonly_role.sql` creates a role with `SELECT`-only privileges
  that the API connects through. SQLite has no equivalent role mechanism, so
  the guardrail parser is the only enforcement point on that path, which is
  why catching AST-level violations (not just top-level statement type)
  matters.

## Database support

`db/engine.py` builds one SQLAlchemy engine per database URL, cached with
`lru_cache`. The rest of the pipeline is database-agnostic: `execute_sql`
branches only on whether the backend name starts with `postgres`, for
statement-timeout handling. BIRD databases are SQLite; the demo schema
targets Postgres through `docker-compose.yml`, with a SQLite-equivalent
build script (`data/build_sqlite_demo.py`) for local development without
Docker.

## Evaluation

`eval/prepare_bird.py` downloads the real BIRD dev set (SQLite databases
plus questions and gold SQL), extracts the nested `dev_databases.zip`, and
slices a configurable subset. `eval/scorer.py` implements execution
accuracy: run the predicted SQL and the gold SQL against the same database,
compare the result sets as unordered rows. `eval/run.py` runs the pipeline
over a subset with the correction loop on or off; `eval/ablation.py` runs
both arms and writes `eval/results/ablation.md`.

## Frontend

`packages/design-tokens` is the single source of truth for color,
typography, spacing, and motion, consumed by both `apps/web` (Tailwind
config) and `apps/landing`. `packages/ui` holds the small set of shared
React primitives (Button, Badge, Card, CodeBlock, Panel) both apps use so
they render identically without duplicating markup.
