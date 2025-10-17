"""
Pydantic schemas for word filtering
"""

from pydantic import BaseModel
from typing import Dict, List


class FilterSpec(BaseModel):
    """Single word filter specification"""

    correct_position: List[int] = []
    incorrect_position: List[int] = []
    incorrect_letter: List[int] = []


class WordFilterRequest(BaseModel):
    """Request model for word filtering"""

    filter_spec: Dict[str, FilterSpec]
