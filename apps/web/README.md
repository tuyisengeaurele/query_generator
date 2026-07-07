# Demo web app

Talks to the pipeline API against the seeded cooperative sales schema
(`cooperatives`, `members`, `products`, `orders`, `order_items`, `payments`).

## Running locally

Start the API first (from the repo root, so `sqlite:///./data/demo.db`
resolves correctly):

```
apps/api/.venv/Scripts/python -m uvicorn app.main:app --app-dir apps/api/src --port 8000
```

Build the local SQLite demo database once, if `data/demo.db` does not exist
yet:

```
apps/api/.venv/Scripts/python data/build_sqlite_demo.py
```

Then start the web app:

```
pnpm --filter web dev
```

The dev server proxies `/api/*` to `http://127.0.0.1:8000`.

Postgres is the schema's target database (see `docker-compose.yml` and
`data/demo_schema.sql`), but this repository was developed without a local
Docker install, so the SQLite path above is what has actually been
exercised end to end.
