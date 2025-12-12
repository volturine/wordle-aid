# Backend

FastAPI service powering the Wordle Aid app. Provides word filtering and definitions, and now exposes a lightweight healthcheck.

## Requirements
- Python 3.11 (see `.python-version` if using a version manager)
- [uv](https://docs.astral.sh/uv/) for dependency management
- SQLite databases under `DB_ROOT_PATH`:
	- `words.db` (contains the word list; required for filtering)
	- `word_definitions.db` (created/updated automatically for cached definitions)

## Environment variables
- `DB_ROOT_PATH` (required): Directory containing `words.db` (and where `word_definitions.db` will be created).
- `RAPID_API_KEY` / `RAPID_API_HOST` (required for definitions): Credentials for WordsAPI.
- `PROD_MODE_ENABLED` (optional): If set, static frontend assets are served from the built `frontend` bundle.

> The app fails fast at import time if `DB_ROOT_PATH` is missing. Set it before running the server or tests, e.g. `export DB_ROOT_PATH=/path/to/database`.

## Install dependencies

```bash
cd backend
uv sync
```

## Run the API locally

```bash
cd backend
export DB_ROOT_PATH=/path/to/database
export RAPID_API_KEY=...      # required for definitions
export RAPID_API_HOST=...     # e.g., wordsapiv1.p.rapidapi.com
uv run uvicorn main:app --reload
```

## Run tests

```bash
cd backend
export DB_ROOT_PATH=$(mktemp -d)  # temp path is fine for healthcheck test
uv run pytest backend/tests
```

## API endpoints (v1)
- `GET /api/health` — readiness/liveness probe (returns `{ status: "ok", timestamp }`).
- `POST /api/filter/five_letter_words` — filter candidate words by Wordle feedback.
- `GET /api/word-definition/{word}` — fetch (and cache) a word definition via WordsAPI.
