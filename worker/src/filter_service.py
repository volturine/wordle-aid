"""Wordle word filtering service (migrated from backend/modules/filter)."""
import logging
from collections import Counter
from functools import lru_cache

from db import d1_all

logger = logging.getLogger(__name__)


class WordleHelper:
    def __init__(self, dictionary: set[str], length: int = 5):
        logger.info(f'Initializing WordleHelper for {length}-letter words ({len(dictionary)} words)')
        self.length = length
        self.dictionary = dictionary

        # For each character, per-position sets of words containing it
        self.processed_dictionary: dict[str, list[set[str]]] = {}
        for word in self.dictionary:
            for pos, char in enumerate(word):
                if char not in self.processed_dictionary:
                    self.processed_dictionary[char] = [set() for _ in range(length)]
                self.processed_dictionary[char][pos].add(word)

    @lru_cache(maxsize=128)  # noqa: B019
    def _filter_characters(
        self,
        guess: str,
        incorrect_position: tuple[int],
        correct_position: tuple[int],
        incorrect_letter: tuple[int],
    ) -> set[str]:
        """Filter words based on Wordle feedback."""
        guess = guess.lower()

        green = {pos: guess[pos] for pos in correct_position}
        yellow = {pos: guess[pos] for pos in incorrect_position}

        confirmed_counts = Counter()
        for letter in green.values():
            confirmed_counts[letter] += 1
        for letter in yellow.values():
            confirmed_counts[letter] += 1

        max_counts = {}
        excluded_at = {}

        for pos in incorrect_letter:
            letter = guess[pos]
            if letter in confirmed_counts:
                max_counts[letter] = confirmed_counts[letter]
                excluded_at.setdefault(letter, set()).add(pos)
            else:
                max_counts[letter] = 0

        def matches(candidate: str) -> bool:
            if any(candidate[pos] != letter for pos, letter in green.items()):
                return False

            cand_counts = Counter(candidate)

            for letter, min_count in confirmed_counts.items():
                if cand_counts[letter] < min_count:
                    return False

            for letter, max_count in max_counts.items():
                if cand_counts[letter] > max_count:
                    return False

            for pos, letter in yellow.items():
                if candidate[pos] == letter:
                    return False

            return all(not any(candidate[pos] == letter for pos in positions) for letter, positions in excluded_at.items())

        if green:
            candidates = set.intersection(
                *[self.processed_dictionary[letter][pos] for pos, letter in green.items()],
                set(self.dictionary),
            )
        else:
            candidates = set(self.dictionary)

        return {word for word in candidates if matches(word)}

    def filter_characters(self, filter_spec: dict) -> list[str]:
        filtered = set(self.dictionary)

        for guess, feedback in filter_spec.items():
            filtered &= self._filter_characters(
                guess,
                incorrect_position=tuple(feedback.get('incorrect_position', [])),
                correct_position=tuple(feedback.get('correct_position', [])),
                incorrect_letter=tuple(feedback.get('incorrect_letter', [])),
            )

        return sorted(filtered)


# Per-isolate cache: key = word length
_wordle_helpers: dict[int, WordleHelper] = {}


async def get_wordle_helper(env, length: int = 5) -> WordleHelper:
    """Get or create the WordleHelper for a length, loading its dictionary from D1."""
    if length not in _wordle_helpers:
        logger.info(f'Loading dictionary for {length}-letter words from D1')
        rows = await d1_all(env.DB, 'SELECT word FROM words WHERE length = ?', length)
        words = {row['word'].lower() for row in rows}
        _wordle_helpers[length] = WordleHelper(words, length)
    return _wordle_helpers[length]
