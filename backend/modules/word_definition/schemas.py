"""
Pydantic schemas for word definitions
"""

from pydantic import BaseModel
from typing import List


class Definition(BaseModel):
    """Single definition entry"""

    definition: str
    partOfSpeech: str


class WordDefinitionResponse(BaseModel):
    """Response model for word definition API"""

    word: str
    definitions: List[Definition]
