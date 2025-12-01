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
    logger.info(f"Received filter request: {request.root}")

    # Convert Pydantic models to dicts for the service
    filter_spec = {
        guess: feedback.model_dump()
        for guess, feedback in request.root.items()
    }

    helper = service.get_wordle_helper(5)
    return helper.filter_characters(filter_spec)
