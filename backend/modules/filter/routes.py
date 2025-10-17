"""
API routes for word filtering
"""

import logging
from fastapi import APIRouter, Request

from . import service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["filter"])


@router.post("/five_letter_words")
async def filter_words(request: Request):
    """
    Filter words based on Wordle game state
    """
    data = await request.json()
    logger.info(f"Received filter request with data: {data}")
    filter_spec = data.get("filter_spec", {})
    helper = service.get_wordle_helper(5)
    filtered = helper.filter_characters(filter_spec)
    return list(filtered)
