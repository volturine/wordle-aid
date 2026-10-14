"""Word definition service (migrated from backend/modules/word_definition).

Cache lives in D1 (definitions table) instead of SQLite on disk.
API calls to RapidAPI go through JS fetch (requests/httpx are not
available in the Workers Python runtime).
"""
import asyncio
import logging
import os
import time

from db import d1_first, d1_run
from memory_cache import InFlight, LruCache, TtlCache, classify_definition
from pyodide.http import pyfetch

logger = logging.getLogger(__name__)

DEFINITION_TIMEOUT_SECONDS = 8
MISS_TTL_SECONDS = 15 * 60
_success_cache = LruCache(256)
_miss_cache = TtlCache(256, MISS_TTL_SECONDS)
_inflight = InFlight()


class DefinitionProviderError(Exception):
    """The definition provider failed. The result is not cached."""


async def get_cached_definition(env, word: str) -> dict | None:
    cached = _success_cache.get(word)
    if cached is not None:
        return cached

    row = await d1_first(env.DB, 'SELECT definition_data FROM definitions WHERE word = ?', word)
    if row:
        import json

        data = json.loads(row['definition_data'])
        _success_cache.set(word, data)
        return data
    return None


async def store_definition(env, word: str, definition_data: dict) -> None:
    import json

    await d1_run(
        env.DB,
        'INSERT INTO definitions (word, definition_data) VALUES (?, ?) '
        'ON CONFLICT (word) DO UPDATE SET definition_data = excluded.definition_data',
        word,
        json.dumps(definition_data),
    )
    _success_cache.set(word, definition_data)
    logger.info(f'Cached definition for word: {word}')


async def _fetch_definition_from_api(env, word: str) -> tuple[int, object]:
    """Fetch word definition from the dictionary API via JS fetch."""
    api_key = getattr(env, 'RAPID_API_KEY', None) or os.environ.get('RAPID_API_KEY', '')
    api_host = getattr(env, 'RAPID_API_HOST', None) or os.environ.get('RAPID_API_HOST', 'wordsapiv1.p.rapidapi.com')
    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': api_host,
    }

    response = await pyfetch(f'https://wordsapiv1.p.rapidapi.com/words/{word}/definitions', headers=headers)
    if response.status != 200:
        return response.status, None
    return response.status, await response.json()


async def _load_definition(env, word: str) -> dict:
    try:
        status, payload = await asyncio.wait_for(
            _fetch_definition_from_api(env, word),
            DEFINITION_TIMEOUT_SECONDS,
        )
    except Exception as exc:
        raise DefinitionProviderError(f'definition lookup failed for {word}') from exc

    kind = classify_definition(status, payload)
    if kind == 'error':
        raise DefinitionProviderError(f'definition provider returned status {status}')
    if kind == 'missing':
        _miss_cache.set(word, True, time.monotonic())
        return {'word': word, 'definitions': []}
    await store_definition(env, word, payload)
    return payload


async def get_word_definition(env, word: str) -> dict:
    """Get word definition - first check D1 cache, then API if not found."""
    logger.info(f'Word definition requested for: {word}')

    cached = await get_cached_definition(env, word)
    if cached is not None:
        logger.info(f'Word definition served from cache for: {word}')
        return cached
    if _miss_cache.get(word, time.monotonic()) is not None:
        return {'word': word, 'definitions': []}

    _future, leader = _inflight.start(word)
    if not leader:
        return await _future
    try:
        result = await _load_definition(env, word)
    except Exception as exc:
        _inflight.fail(word, exc)
        raise
    _inflight.succeed(word, result)
    return result
