# Contributing to Wordle Aid

Thanks for your interest in improving Wordle Aid. This guide covers how to develop
locally, what we expect in pull requests, and how deployments work.

By participating, you agree to follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Ways to help

- Fix bugs and improve the word-filtering logic
- Polish the frontend UX and mobile PWA experience
- Improve documentation and self-hosting guidance
- Report security issues privately (see [SECURITY.md](SECURITY.md))

Please open an issue before large architectural changes so we can align on scope.

## Development setup

### Requirements

- **Node.js 22** (see [`.nvmrc`](.nvmrc))
- npm (comes with Node)
- **Python 3.12+** and [uv](https://docs.astral.sh/uv/) for the worker

### Install and run

```sh
git clone https://github.com/volturine/wordle-aid.git
cd wordle-aid/frontend
npm install
npm run dev
```

The frontend talks to `/api/...`; for a full stack with the real API, run the
worker locally and point your browser at it:

```sh
cd ../worker
uv sync
uv run pywrangler dev          # http://localhost:8787 (local D1 + assets)
```

`npm run dev` proxies `/api` to that worker; set `WORKER_ORIGIN` if it runs
elsewhere.

See [`worker/README.md`](worker/README.md) for seeding the local D1 database.

### Architecture in one paragraph

`worker/` is the only deployable artifact: a Cloudflare **Python Worker** that
serves the SvelteKit static build (Workers Static Assets) and the API from the
same origin. `POST /api/filter/five_letter_words` filters the dictionary in D1
by Wordle feedback; `GET /api/word-definition/{word}` serves definitions from a
D1 cache with a RapidAPI fallback. `backend/` is the retired FastAPI app, kept
for reference and tests.

Read [`AGENTS.md`](AGENTS.md) for the runtime constraints (Python Workers have
no `sqlite3`/`requests`/`httpx`, no FastAPI at import time, startup CPU limits)
and the D1 data policy before touching the worker.

### Validate before you push

```sh
python3 -m py_compile worker/src/*.py   # worker syntax
cd frontend && npm run build            # frontend build
cd ../worker && uv sync                 # worker deps resolve
```

CI runs the same checks plus `wrangler deploy --dry-run` for both environments.

## Pull requests

- Keep PRs focused; one logical change per PR.
- Master is deployed to production on push — every PR must leave CI green.
- Use the PR template; note anything touching D1 data or the worker startup path.

### Preview deployments

PRs can be deployed to [dev.wordle-aid.com](https://dev.wordle-aid.com) by
adding the `deploy-dev` label (same-repo PRs only; the PR must be the sole
open PR with that label). Dev shares the same schema but has its own D1
database; deploys never import data.

## License

By contributing, you agree that your contributions will be licensed under the
[MIT License](LICENSE).
