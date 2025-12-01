from pydantic import BaseModel


class Definition(BaseModel):
    """Single definition entry."""

    definition: str
    partOfSpeech: str


class WordDefinitionResponse(BaseModel):
    """Response model for word definition API."""

    word: str
    definitions: list[Definition]
