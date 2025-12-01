import logging
from collections import Counter
from functools import lru_cache

from .models import load_words_by_length

logger = logging.getLogger(__name__)


class WordleHelper:
    def __init__(self, length: int = 5):
        logger.info(f'Initializing WordleHelper for {length}-letter words')
        self.length = length
        self._set_dictionary(length=length)

    def _set_dictionary(self, length: int = 5) -> None:
        """Load dictionary from database using models."""
        # Load words from database via models
        words = load_words_by_length(length)
        self.dictionary = words

        # Process the dictionary to create dictionary of characters where for each character there will be up to length lists of words
        self.processed_dictionary = {}
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
        """Filter words based on Wordle feedback.

        Args:
            guess: The guessed word
            incorrect_position: Positions where letter is in word but wrong spot
            correct_position: Positions where letter is correct
            incorrect_letter: Positions where letter is not in word (or not at this position)
        """
        guess = guess.lower()

        # Build constraint maps
        green = {pos: guess[pos] for pos in correct_position}
        yellow = {pos: guess[pos] for pos in incorrect_position}

        # Count confirmed instances of each letter (Green + Yellow)
        confirmed_counts = Counter()
        for letter in green.values():
            confirmed_counts[letter] += 1
        for letter in yellow.values():
            confirmed_counts[letter] += 1

        # Determine max counts allowed and excluded positions
        max_counts = {}
        excluded_at = {}

        for pos in incorrect_letter:
            letter = guess[pos]
            if letter in confirmed_counts:
                # It's a confirmed letter, but this specific instance is Grey.
                # This implies the target has exactly confirmed_counts[letter] of this letter.
                max_counts[letter] = confirmed_counts[letter]

                # Also, this letter cannot be at this position
                excluded_at.setdefault(letter, set()).add(pos)
            else:
                # Not confirmed anywhere. Count is 0.
                max_counts[letter] = 0

        def matches(candidate: str) -> bool:
            # Green: letter must be at exact position
            if any(candidate[pos] != letter for pos, letter in green.items()):
                return False

            cand_counts = Counter(candidate)

            # Check min counts (confirmed letters must exist at least that many times)
            for letter, min_count in confirmed_counts.items():
                if cand_counts[letter] < min_count:
                    return False

            # Check max counts
            for letter, max_count in max_counts.items():
                if cand_counts[letter] > max_count:
                    return False

            # Yellow: letter must exist but NOT at this position
            for pos, letter in yellow.items():
                if candidate[pos] == letter:
                    return False

            # Excluded positions: confirmed letter must not be at grey position
            return all(not any(candidate[pos] == letter for pos in positions) for letter, positions in excluded_at.items())

        # Fast initial filter using pre-indexed green letters
        if green:
            candidates = set.intersection(
                *[self.processed_dictionary[letter][pos] for pos, letter in green.items()],
                set(self.dictionary),
            )
        else:
            candidates = set(self.dictionary)

        return {word for word in candidates if matches(word)}

    def filter_characters(self, filter_spec: dict) -> list[str]:
        """Filter words based on multiple guesses and their feedback.

        Args:
            filter_spec: Dict mapping guessed words to their GuessFilter objects:
                {
                    "LEAST": GuessFilter(
                        correct_position=[2, 4],
                        incorrect_position=[],
                        incorrect_letter=[0, 1, 3]
                    )
                }
        """
        filtered = set(self.dictionary)

        for guess, feedback in filter_spec.items():
            filtered &= self._filter_characters(
                guess,
                incorrect_position=tuple(feedback.incorrect_position),
                correct_position=tuple(feedback.correct_position),
                incorrect_letter=tuple(feedback.incorrect_letter),
            )

        return sorted(filtered)


# Global instance
_wordle_helper = None


def get_wordle_helper(length: int = 5) -> WordleHelper:
    """Get or create WordleHelper instance."""
    global _wordle_helper
    if _wordle_helper is None:
        _wordle_helper = WordleHelper(length)
    return _wordle_helper
