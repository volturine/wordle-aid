"""Wordle Aid — Cloudflare Python Worker.

FastAPI app providing the API, with the SvelteKit static build served
from Workers Static Assets. Data lives in D1 instead of local SQLite.

Local dev:  uv run pywrangler dev
Deploy:     uv run pywrangler deploy
"""
import datetime
import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response

import filter_service
import word_definition_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title='Wordle Aid API', version='2.0.0')


@app.get('/api/health')
async def health() -> dict[str, str]:
    """Lightweight healthcheck endpoint for readiness/liveness probes."""
    return {'status': 'ok', 'timestamp': datetime.datetime.now(datetime.UTC).isoformat()}


@app.post('/api/filter/five_letter_words')
async def filter_words(request: Request) -> list[str]:
    """Filter words based on Wordle game state."""
    body = await request.json()
    filter_spec = body.get('filter_spec', {})

    env = request.scope['env']
    helper = await filter_service.get_wordle_helper(env, 5)
    return helper.filter_characters(filter_spec)


@app.get('/api/word-definition/{word}')
async def get_word_definition(word: str, request: Request) -> dict:
    """Get word definition - first check D1 cache, then API if not found."""
    word = word.lower()
    if not word.isalpha() or len(word) > 32:
        raise HTTPException(status_code=400, detail='Invalid word')

    env = request.scope['env']
    try:
        return await word_definition_service.get_word_definition(env, word)
    except Exception:
        raise HTTPException(status_code=500, detail='Error fetching definition') from None


# Safety net: with run_worker_first = ["/api/*"], static assets are served
# directly by Workers Assets and this route is never hit. It keeps the
# worker functional if run_worker_first is ever set to true instead.
@app.get('/{full_path:path}')
async def frontend(full_path: str, request: Request):
    env = request.scope['env']
    resp = await env.ASSETS.fetch(f'https://assets.local/{full_path}')
    body = await resp.bytes()
    return Response(
        content=body,
        status_code=resp.status,
        media_type=resp.headers.get('content-type', 'text/html'),
    )


from workers import asgi  # noqa: E402

Default = asgi.entrypoint(app)
