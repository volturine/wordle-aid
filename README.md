# Wordle Aid

A Wordle helper: word filtering from game feedback + word definitions.

- `frontend/` — SvelteKit + Tailwind frontend (static build, PWA)
- `backend/` — legacy FastAPI backend (kept for reference/tests; replaced by the worker below)
- `worker/` — Cloudflare Python Worker (FastAPI on Workers + D1 + static assets) — **this is what gets deployed**
- `database/` — original SQLite databases (source of truth for D1 imports)

## Deploying

See [worker/README.md](worker/README.md).

```bash
cd worker
npx wrangler d1 create wordle-aid   # once; paste database_id into wrangler.toml
./scripts/migrate_to_d1.sh          # once; imports words + definitions into D1
./scripts/build_frontend.sh         # builds frontend -> worker/public
uv run pywrangler deploy
```

The old Docker image / docker-compose / Watchtower setup has been removed —
the Cloudflare Worker replaces the whole stack (API + static frontend + database).
