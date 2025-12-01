"""
API routes for word filtering
"""

import logging
from fastapi import APIRouter

from . import service
from .schemas import WordFilterRequest

logger = logging.getLogger(__name__)

router = APIRouter(tags=["filter"])


@router.post("/five_letter_words")
async def filter_words(request: WordFilterRequest) -> list[str]:
    """
    Filter words based on Wordle game state.

    Submit guessed words with their color feedback to get matching words.
    """
    logger.info(f"Received filter request: {request.json()}")


    helper = service.get_wordle_helper(5)
    return helper.filter_characters(request.filter_spec)