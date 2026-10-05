"""Word definition service (migrated from backend/modules/word_definition).

Cache lives in D1 (definitions table) instead of SQLite on disk.
API calls to RapidAPI go through JS fetch (requests/httpx are not
available in the Workers Python runtime).
"""
import logging
import os

from db import d1_first, d1_run
from js import Object, fetch
from pyodide.ffi import to_js as _to_js

logger = logging.getLogger(__name__)

# Per-isolate response cache to avoid repeat D1/API hits
_definition_cache: dict[str, dict] = {}


def _to_js(obj):
    return _to_js(obj, dict_converter=Object.fromEntries)


async def get_cached_definition(env, word: str) -> dict | None:
    if word in _definition_cache:
        return _definition_cache[word]

    row = await d1_first(env.DB, 'SELECT definition_data FROM definitions WHERE word = ?', word)
    if row:
        import json

        data = json.loads(row['definition_data'])
        _definition_cache[word] = data
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
    _definition_cache[word] = definition_data
    logger.info(f'Cached definition for word: {word}')


async def _fetch_definition_from_api(env, word: str) -> dict:
    """Fetch word definition from the dictionary API via JS fetch."""
    api_key = getattr(env, 'RAPID_API_KEY', None) or os.environ.get('RAPID_API_KEY', '')
    api_host = getattr(env, 'RAPID_API_HOST', None) or os.environ.get('RAPID_API_HOST', 'wordsapiv1.p.rapidapi.com')
    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': api_host,
    }

    response = await fetch(f'https://wordsapiv1.p.rapidapi.com/words/{word}/definitions', _to_js({'headers': headers}))
    if not response.ok:
        raise RuntimeError(f'API returned status {response.status}')
    return (await response.json()).to_py()


async def get_word_definition(env, word: str) -> dict:
    """Get word definition - first check D1 cache, then API if not found."""
    logger.info(f'Word definition requested for: {word}')

    cached = await get_cached_definition(env, word)
    if cached:
        logger.info(f'Word definition served from cache for: {word}')
        return cached

    try:
        result = await _fetch_definition_from_api(env, word)
        await store_definition(env, word, result)
        logger.info(f'Word definition served from API and cached for: {word}')
        return result
    except Exception as e:
        logger.error(f"Error fetching definition for '{word}': {e}")
        raise
