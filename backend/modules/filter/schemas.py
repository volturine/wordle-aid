from pydantic import BaseModel, Field


class GuessFilter(BaseModel):
    """Filter specification for a single guessed word.

    Each list contains position indices (0-4) indicating the feedback color:
    - correct_position: Letter is correct at this position
    - incorrect_position: Letter exists in word but wrong position
    - incorrect_letter: Letter is not in word (or not at this position if also correct/incorrect position)
    """

    correct_position: list[int] = Field(default=[], description='Positions where letter is correct (green)')
    incorrect_position: list[int] = Field(default=[], description='Positions where letter exists but wrong spot (yellow)')
    incorrect_letter: list[int] = Field(default=[], description='Positions where letter is not in word (grey)')

    model_config = {
        'json_schema_extra': {
            'examples': [
                {
                    'correct_position': [2, 4],
                    'incorrect_position': [],
                    'incorrect_letter': [0, 1, 3],
                }
            ]
        }
    }


class WordFilterRequest(BaseModel):
    """Request model for word filtering.

    The request body is a dictionary where:
    - Key: The guessed word (e.g., "ADAPT")
    - Value: The color feedback for each position
    """

    filter_spec: dict[str, GuessFilter]

    model_config = {
        'json_schema_extra': {
            'examples': [
                {
                    'filter_spec': {
                        'LEAST': {
                            'correct_position': [2, 4],
                            'incorrect_position': [],
                            'incorrect_letter': [0, 1, 3],
                        },
                        'ADAPT': {
                            'correct_position': [2, 4],
                            'incorrect_position': [],
                            'incorrect_letter': [0, 1, 3],
                        },
                    }
                }
            ]
        }
    }
