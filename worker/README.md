# Wordle Aid — Cloudflare Python Worker

Migration of the Dockerized FastAPI backend to a Cloudflare Python Worker,
with D1 replacing the local SQLite databases and the SvelteKit static build
served directly from Workers Static Assets.

## Layout

```
worker/
├── src/
│   ├── worker.py                    # FastAPI app + asgi entrypoint
│   ├── db.py                        # D1 helpers (Pyodide FFI)
│   ├── filter_service.py            # wordle filter (was backend/modules/filter)
│   └── word_definition_service.py   # definitions cache + RapidAPI (was backend/modules/word_definition)
├── migrations/                      # generated SQL from local SQLite (data)
├── scripts/
│   ├── export_db.py                 # sqlite -> D1 SQL export
│   ├── build_frontend.sh            # builds frontend -> worker/public
│   └── migrate_to_d1.sh             # one-time D1 setup + data import
├── public/                          # frontend static build (generated, gitignore)
├── pyproject.toml                   # python worker deps (fastapi, workers-py)
└── wrangler.toml
```

## One-time migration

```bash
cd worker

# 1. Create the D1 database and copy its database_id into wrangler.toml
npx wrangler d1 create wordle-aid

# 2. Export local data + apply schema/import + set secret
./scripts/migrate_to_d1.sh
```

## Local development

```bash
cd frontend && npm install && npm run build
rm -rf ../worker/public && cp -R build ../worker/public   # or run ../worker/scripts/build_frontend.sh
cd ../worker
uv sync                 # first time only
uv run pywrangler dev   # local D1 + assets on http://localhost:8787
```

The frontend talks to `/api/...` (same origin) — no code changes needed.

## Deploy

```bash
./scripts/build_frontend.sh
cd worker && uv run pywrangler deploy
```

## Secrets / vars

- `RAPID_API_KEY` — secret: `uv run pywrangler secret put RAPID_API_KEY`
- `RAPID_API_HOST` — plain var in `wrangler.toml`

## Notes / gotchas

- `sqlite3`, `requests` and `httpx` are **not available** in the Python Workers
  runtime; D1 is accessed via `env.DB` (JS interop) and outbound HTTP via JS `fetch`.
- The word dictionary is loaded from D1 once per isolate and cached in memory
  (`_wordle_helpers`), same behaviour as the old global singleton.
- The Docker image, docker-compose, Watchtower label and DB volume are all
  replaced by this worker — nothing to keep running on the VPS.
- `not_found_handling = "404-page"` serves the SvelteKit 404 fallback for
  unknown routes.
