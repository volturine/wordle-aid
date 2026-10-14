"""Validate filter requests without framework imports."""
import re

MAX_CONSTRAINTS = 6
MAX_BODY_CHARS = 8192
DEFAULT_LIMIT = 100
MAX_LIMIT = 200
MAX_OFFSET = 20000

_GUESS = re.compile(r'[a-z_]{5}')
_GROUPS = ('correct_position', 'incorrect_position', 'incorrect_letter')


def parse_constraints(body: object) -> list[dict]:
    """Return the constraints that actually mark a square.

    Rows with no marked squares are omitted. An empty result means the caller
    has not given a clue yet.
    """
    if not isinstance(body, dict):
        raise ValueError('Body must be an object')
    raw = body.get('constraints')
    if not isinstance(raw, list):
        raise ValueError("Body must contain a 'constraints' array")
    if len(raw) > MAX_CONSTRAINTS:
        raise ValueError('At most 6 guesses can be filtered at once')

    constraints = []
    for index, item in enumerate(raw, start=1):
        if not isinstance(item, dict):
            raise ValueError(f'Guess {index} must be an object')
        guess = item.get('guess')
        if not isinstance(guess, str) or _GUESS.fullmatch(guess.lower()) is None:
            raise ValueError(f'Guess {index} must be 5 letters, using _ for an empty square')
        guess = guess.lower()
        seen: set[int] = set()
        groups: dict[str, list[int]] = {}
        for key in _GROUPS:
            values = item.get(key, [])
            if not isinstance(values, list):
                raise ValueError(f'Guess {index} {key} must be an array of positions')
            cleaned = []
            for pos in values:
                if isinstance(pos, bool) or not isinstance(pos, int) or not 0 <= pos <= 4:
                    raise ValueError(f'Guess {index} positions must be integers from 0 to 4')
                if pos in seen:
                    raise ValueError(f'Guess {index} uses position {pos} more than once')
                if guess[pos] == '_':
                    raise ValueError(f'Guess {index} marks an empty square')
                seen.add(pos)
                cleaned.append(pos)
            groups[key] = cleaned
        if seen:
            constraints.append({'guess': guess, **groups})
    return constraints


def parse_page(body: dict) -> tuple[int, int, int]:
    limit = _page_number(body, 'limit', DEFAULT_LIMIT)
    answer_offset = _page_number(body, 'answer_offset', 0)
    guess_offset = _page_number(body, 'guess_offset', 0)
    if not 1 <= limit <= MAX_LIMIT:
        raise ValueError(f'limit must be an integer from 1 to {MAX_LIMIT}')
    if answer_offset > MAX_OFFSET or guess_offset > MAX_OFFSET:
        raise ValueError('offset is too large')
    return limit, answer_offset, guess_offset


def _page_number(body: dict, key: str, default: int) -> int:
    if key not in body:
        return default
    value = body[key]
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f'{key} must be a non-negative integer')
    return value
