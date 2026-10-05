# Wordle Aid

**Wordle Aid** is your daily Wordle helper: enter your guesses with their color
feedback and instantly see every word that still fits, plus definitions for the
remaining candidates.

Visit [wordle-aid.com](https://wordle-aid.com).

[![CI/CD](https://github.com/volturine/wordle-aid/actions/workflows/ci-cd.yaml/badge.svg)](https://github.com/volturine/wordle-aid/actions/workflows/ci-cd.yaml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## Features

- **Smart filtering** — enter each guess with green/yellow/grey feedback and get
  every remaining candidate word, handling duplicate letters correctly
- **Definitions** — look up any remaining candidate's definition on the spot
- **PWA** — installable, offline-friendly shell; your game state lives in your browser
- **No accounts, no tracking** — the server stores a static dictionary and a
  definitions cache, nothing else

## How it works

One Cloudflare Worker does everything:

| Layer | What it does |
| --- | --- |
| **Frontend** | SvelteKit + Tailwind static build (PWA) served from Workers Static Assets |
| **API** | Python Worker (`worker/src/`) — filtering + definitions on the same origin |
| **Database** | Cloudflare D1 — static `words` dictionary + runtime `definitions` cache |
| **CI/CD** | GitHub Actions — every PR validated; PRs labeled `deploy-dev` deploy to [dev.wordle-aid.com](https://dev.wordle-aid.com); `master` deploys [wordle-aid.com](https://wordle-aid.com) |

Endpoints:

- `POST /api/filter/five_letter_words` — feedback map → remaining candidate words
- `GET /api/word-definition/{word}` — definition (D1 cache, then WordsAPI)
- `GET /api/health` — healthcheck

## Quick start (development)

Requirements: Node.js 22 (see [`.nvmrc`](.nvmrc)), Python 3.12+, [uv](https://docs.astral.sh/uv/).

```sh
git clone https://github.com/volturine/wordle-aid.git
cd wordle-aid/frontend
npm install && npm run build       # static build

cd ../worker
uv sync
uv run pywrangler dev              # full stack on http://localhost:8787
```

See [`worker/README.md`](worker/README.md) for seeding local D1 and
[`CONTRIBUTING.md`](CONTRIBUTING.md) for the full guide.

## Self-hosting your own

```sh
cd worker
npx wrangler d1 create wordle-aid          # copy database_id into wrangler.toml
./scripts/migrate_to_d1.sh                 # seed the dictionary (one-time)
uv run pywrangler secret put RAPID_API_KEY # optional: enables definitions
./scripts/build_frontend.sh
uv run pywrangler deploy
```

## Repository layout

- `frontend/` — SvelteKit + Tailwind static frontend (PWA)
- `worker/` — Cloudflare Python Worker: API, assets, D1 (`worker/README.md`)
- `backend/` — retired FastAPI backend, kept for reference and tests
- `database/` — original SQLite files; source of truth for D1 imports
- [`AGENTS.md`](AGENTS.md) — working guide for agents and humans (runtime constraints, data policy, principles)

## License

[MIT](LICENSE) — © 2026 Roland Rajcsanyi. Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).
