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
from request_validation import MAX_BODY_CHARS, parse_constraints, parse_page
from word_definition_service import DefinitionProviderError

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
        try:
            helper = await filter_service.get_wordle_helper(env, 5)
        except Exception:
            logger.exception('Dictionary is not ready')
            return json_response({'status': 'not_ready', 'detail': 'Word bank is unavailable'}, 503)
        return json_response({
            'status': 'ok',
            'timestamp': datetime.datetime.now(datetime.UTC).isoformat(),
            'bank_version': helper.version,
            'guess_count': len(helper.dictionary),
            'answer_count': len(helper.answers),
        })

    # --- Word filter ---
    if path == '/api/filter/five_letter_words' and method == 'POST':
        try:
            raw = await request.text()
        except Exception:
            return json_response({'detail': 'Invalid JSON body'}, 400)
        if len(raw) > MAX_BODY_CHARS:
            return json_response({'detail': 'Request body is too large'}, 400)
        try:
            body = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            return json_response({'detail': 'Invalid JSON body'}, 400)
        try:
            constraints = parse_constraints(body)
            limit, answer_offset, guess_offset = parse_page(body)
        except ValueError as exc:
            return json_response({'detail': str(exc)}, 400)

        try:
            helper = await filter_service.get_wordle_helper(env, 5)
        except Exception:
            logger.exception('Dictionary is not ready')
            return json_response({'status': 'not_ready', 'detail': 'Word bank is unavailable'}, 503)
        return json_response(helper.filter_page(constraints, limit, answer_offset, guess_offset))

    # --- Word definitions ---
    if path.startswith('/api/word-definition/') and method == 'GET':
        word = path[len('/api/word-definition/'):].strip('/').lower()
        if not word or not word.isalpha() or len(word) > MAX_WORD_LENGTH:
            return json_response({'detail': 'Invalid word'}, 400)

        try:
            result = await word_definition_service.get_word_definition(env, word)
        except DefinitionProviderError:
            logger.exception(f"Definition provider failed for '{word}'")
            return json_response({'detail': 'Definition provider is unavailable'}, 502)
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
