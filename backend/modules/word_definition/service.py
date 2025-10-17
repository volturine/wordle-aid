"""
Business logic for word definitions
"""

import logging
import os
from functools import lru_cache

import requests
from fastapi import HTTPException

from .models import get_cached_definition, store_definition

logger = logging.getLogger(__name__)


@lru_cache(maxsize=128)
def _get_word_definition_from_api(word: str) -> dict:
    """
    Fetch word definition from dictionary API
    """
    headers = {
        "x-rapidapi-key": os.environ.get("RAPID_API_KEY", ""),
        "x-rapidapi-host": os.environ.get("RAPID_API_HOST", "wordsapiv1.p.rapidapi.com"),
    }

    response = requests.get(f"https://wordsapiv1.p.rapidapi.com/words/{word}/definitions", headers=headers)
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch word definition")
    return response.json()


async def get_word_definition(word: str) -> dict:
    """
    Get word definition - first check SQLite cache, then API if not found
    """
    logger.info(f"Word definition requested for: {word}")

    # First, try to get from cache
    cached_result = get_cached_definition(word)
    if cached_result:
        logger.info(f"Word definition served from cache for: {word}")
        return cached_result

    try:
        result = _get_word_definition_from_api(word)
        store_definition(word, result)
        logger.info(f"Word definition served from API and cached for: {word}")
        return result
    except requests.RequestException as e:
        logger.error(f"Request exception while fetching definition for '{word}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching definition: {str(e)}")
    except HTTPException:
        # Re-raise HTTPExceptions as they already contain proper error info
        raise
