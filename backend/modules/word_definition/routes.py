from fastapi import APIRouter

from . import service

router = APIRouter(tags=['words'])


@router.get('/{word}')
async def get_word_definition_route(word: str):
    """Get word definition endpoint."""
    return await service.get_word_definition(word)
