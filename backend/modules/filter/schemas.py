"""
Pydantic schemas for word filtering
"""

from pydantic import BaseModel, Field, RootModel


class GuessFilter(BaseModel):
    """
    Filter specification for a single guessed word.

    Each list contains position indices (0-4) indicating the feedback color:
    - green_positions: Letter is correct at this position
    - yellow_positions: Letter exists in word but wrong position
    - grey_positions: Letter is not in word (or not at this position if also green/yellow)
    """

    green_positions: list[int] = Field(
        default=[], description="Positions where letter is correct (green)"
    )
    yellow_positions: list[int] = Field(
        default=[], description="Positions where letter exists but wrong spot (yellow)"
    )
    grey_positions: list[int] = Field(
        default=[], description="Positions where letter is not in word (grey)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "green_positions": [2, 4],
                    "yellow_positions": [],
                    "grey_positions": [0, 1, 3],
                }
            ]
        }
    }


class WordFilterRequest(BaseModel):
    """
    Request model for word filtering.

    The request body is a dictionary where:
    - Key: The guessed word (e.g., "ADAPT")
    - Value: The color feedback for each position
    """

    filter_spec: dict[str, GuessFilter]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "filter_spec": {
                        "LEAST": {
                            "green_positions": [2, 4],
                            "yellow_positions": [],
                            "grey_positions": [0, 1, 3],
                        },
                        "ADAPT": {
                            "green_positions": [2, 4],
                            "yellow_positions": [],
                            "grey_positions": [0, 1, 3],
                        },
                    }
                }
            ]
        }
    }
