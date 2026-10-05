"""Wordle Aid — Cloudflare Python Worker.

Hand-rolled router on the workers SDK instead of FastAPI: FastAPI + Pydantic
imports exceed the Workers startup CPU limit for this small API. Data lives
in D1, and the SvelteKit static build is served from Workers Static Assets.

Local dev:  uv run pywrangler dev
Deploy:     uv run pywrangler deploy [--env dev]
"""
import datetime
import json
import logging

from workers import WorkerEntrypoint, Response

import filter_service
import word_definition_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_WORD_LENGTH = 32


def json_response(data, status: int = 200) -> Response:
    return Response.json(data) if status == 200 else Response(
        json.dumps(data), status, headers={'Content-Type': 'application/json'}
    )


async def handle(request, env) -> Response:
    url = request.url
    path = url.split('?', 1)[0].split('://', 1)[-1].split('/', 1)
    path = '/' + (path[1] if len(path) > 1 else '')
    method = request.method.value if hasattr(request.method, 'value') else str(request.method)

    # --- Health ---
    if path == '/api/health' and method == 'GET':
        return json_response({'status': 'ok', 'timestamp': datetime.datetime.now(datetime.UTC).isoformat()})

    # --- Word filter ---
    if path == '/api/filter/five_letter_words' and method == 'POST':
        try:
            body = await request.json()
        except Exception:
            return json_response({'detail': 'Invalid JSON body'}, 400)
        if not isinstance(body, dict) or not isinstance(body.get('filter_spec'), dict):
            return json_response({'detail': "Body must contain a 'filter_spec' object"}, 400)

        helper = await filter_service.get_wordle_helper(env, 5)
        return json_response(helper.filter_characters(body['filter_spec']))

    # --- Word definitions ---
    if path.startswith('/api/word-definition/') and method == 'GET':
        word = path[len('/api/word-definition/'):].strip('/').lower()
        if not word or not word.isalpha() or len(word) > MAX_WORD_LENGTH:
            return json_response({'detail': 'Invalid word'}, 400)

        try:
            result = await word_definition_service.get_word_definition(env, word)
        except Exception:
            logger.exception(f"Failed to fetch definition for '{word}'")
            return json_response({'detail': 'Error fetching definition'}, 500)
        return json_response(result)

    # --- Static assets (safety net; assets normally served before the worker) ---
    if path.startswith('/api/'):
        return json_response({'detail': 'Not found'}, 404)

    js_resp = await env.ASSETS.fetch(url)
    return Response(js_resp)


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        return await handle(request, self.env)
