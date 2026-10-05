# Wordle Aid

A Wordle helper that filters the remaining possible answers from game feedback and shows word definitions: SvelteKit static frontend, Python Worker API, D1 database — deployed as a single Cloudflare Worker.

**Stack:** Python 3.12 (Workers/Pyodide) · SvelteKit 5 + TypeScript · Tailwind · Cloudflare D1 + Workers Static Assets · uv · npm

Visit [wordle-aid.com](https://wordle-aid.com). Development preview at [dev.wordle-aid.com](https://dev.wordle-aid.com).

## Layout

- `frontend/` — SvelteKit + Tailwind static build (PWA), the only UI
- `worker/` — the deployed Cloudflare Python Worker (API + static assets + D1)
- `backend/` — legacy FastAPI backend, kept for reference and tests only; the worker replaced it
- `database/` — original SQLite databases; source of truth for D1 imports (never edited at runtime)

## Commands

```bash
# Frontend
cd frontend && npm install && npm run dev   # dev server
npm run build                               # production static build -> frontend/build

# Worker (Python)
cd worker
uv sync                                     # install workers-py + workers-runtime-sdk
uv run pywrangler dev                       # local dev (local D1 + assets) on :8787
uv run pywrangler deploy                    # deploy production (wordle-aid.com)
uv run pywrangler deploy --env dev          # deploy development (dev.wordle-aid.com)

# Backend tests (legacy logic)
cd backend && uv run pytest tests
```

Full frontend build + staging into the worker: `worker/scripts/build_frontend.sh`.

## Deployment model (GitHub Actions, mirrors scrapscache)

- Every PR: `validate` — frontend build, python syntax check, `wrangler deploy --dry-run` for both envs
- PR labeled `deploy-dev`: `deploy-cloudflare-dev` — redeploys `dev.wordle-aid.com` (schema-only D1 apply, no data import)
- Push to `master`: `deploy-cloudflare-production` — deploys `wordle-aid.com` + post-deploy healthcheck on `/api/health`
- Required repo secrets: `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`, `RAPID_API_KEY`
- `master` is the source of truth; never commit directly — open a PR

## D1 data policy (read before touching data)

- `words` is a **static dictionary** (15,921 rows at `length = 5`) imported **once**, manually, via `worker/scripts/migrate_to_d1.sh`. CI deploys never import data — only `migrations/0000_schema.sql`.
- `definitions` is a runtime cache: on a miss the worker fetches RapidAPI and writes the row. Never bulk-import definitions in CI; it would clobber live cache entries with stale local data.
- All generated seed SQL uses `INSERT ... ON CONFLICT (word) DO NOTHING`: re-importing writes 0 rows. D1 counts every rewritten row in `rows_written`, and the free tier allows 100k/day.
- Regenerate seed SQL with `worker/scripts/export_db.py` after changing `database/*.db` (default: 5-letter words; pass `--lengths 3 4 5 ...` for more).

## Python Workers runtime constraints (hard rules)

- No `sqlite3`, `requests`, `httpx`, or any package with native/Rust extensions. D1 goes through the `env.DB` binding (see `worker/src/db.py`); outbound HTTP uses `pyodide.http.pyfetch` (plain `js.fetch` needs `to_js`, which this runtime does not support with `dict_converter`).
- No FastAPI/Pydantic at import time: their imports blow the **startup CPU limit** (1347ms > 1000ms). The worker is a hand-rolled router on the `workers` SDK (`worker/src/worker.py`). Keep it that way; do not reintroduce framework imports at module level.
- Everything at module scope runs at isolate start: keep imports and module-level work minimal.
- D1 rejects `BEGIN TRANSACTION`/`COMMIT` in `wrangler d1 execute --file` imports.

## Endpoints

- `GET /api/health` — healthcheck (CI verifies prod after deploy)
- `POST /api/filter/five_letter_words` — body `{"filter_spec": {"GUESS": {"correct_position": [...], "incorrect_position": [...], "incorrect_letter": [...]}}}` → remaining candidate words
- `GET /api/word-definition/{word}` — D1 cache first, then RapidAPI (`RAPID_API_KEY` secret), then cached to D1

The frontend calls `/api/...` same-origin; never introduce a separate API origin or CORS setup.

## Definition of done

`python3 -m py_compile worker/src/*.py` + frontend build must pass before done or review. CI must be green on the PR. Fix failures and warnings immediately (pre-existing ones when you touch the area).

## Principles

- Do not preserve backward compatibility. Remove obsolete paths instead of adding compatibility layers, fallbacks, or migrations.
- Choose the simplest implementation that fully meets the current requirements. Avoid speculative abstractions, configuration, and indirection.
- Grow the system in layers. Start from the smallest version that works end to end, and add each new capability on top of a product that already works. Never trade a working product for unfinished complexity.
- Keep components modular and concerns clearly separated.
- Prefer established, well-maintained libraries when they reduce overall complexity or improve reliability. Do not reimplement common functionality without a clear reason.
- Lean on the dependencies already in the project before writing your own implementation or adding packages. Do not assume a library lacks a capability without checking its documentation and types.
- Make architectural decisions for the long term. Do not accept a stopgap that only works for now and is meant to be replaced later.

## Problem solving

- Start from the intended outcome, then trace the behavior across every relevant layer before changing code.
- Form a causal explanation and actively look for evidence that disproves it.
- Fix the cause where the responsibility belongs. Prefer clear ownership and isolation boundaries over patches at the point where symptoms appear.
- When one fix reveals another failure, investigate it independently instead of forcing it into the previous explanation.
- Before finishing, be able to explain the root cause, why the symptoms were misleading, what now prevents recurrence, and what evidence proves the fix.
