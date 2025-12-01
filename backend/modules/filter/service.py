"""
Business logic for word filtering using WordleHelper
"""

from functools import lru_cache
import logging

from .models import load_words_by_length

logger = logging.getLogger(__name__)


class WordleHelper:
    def __init__(self, length: int = 5):
        logger.info(f"Initializing WordleHelper for {length}-letter words")
        self.length = length
        self._set_dictionary(length=length)

    def _set_dictionary(self, length: int = 5) -> None:
        """Load dictionary from database using models"""
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

    @lru_cache(maxsize=128)
    def _filter_characters(
        self,
        guess: str,
        yellow_positions: tuple[int],
        green_positions: tuple[int],
        grey_positions: tuple[int],
    ) -> set[str]:
        """
        Filter words based on Wordle feedback.

        Args:
            guess: The guessed word
            yellow_positions: Positions where letter is in word but wrong spot
            green_positions: Positions where letter is correct
            grey_positions: Positions where letter is not in word (or not at this position)
        """
        guess = guess.lower()

        # Build constraint maps
        green = {pos: guess[pos] for pos in green_positions}
        yellow = {pos: guess[pos] for pos in yellow_positions}

        # Letters confirmed to exist in the word
        confirmed_letters = set(green.values()) | set(yellow.values())

        # Grey letters not confirmed elsewhere = completely absent from word
        absent_letters = {guess[pos] for pos in grey_positions if guess[pos] not in confirmed_letters}

        # Grey positions for confirmed letters (e.g., A is green at pos 3, grey at pos 1)
        excluded_at = {}
        for pos in grey_positions:
            letter = guess[pos]
            if letter in confirmed_letters:
                excluded_at.setdefault(letter, set()).add(pos)

        def matches(candidate: str) -> bool:
            # Green: letter must be at exact position
            if any(candidate[pos] != letter for pos, letter in green.items()):
                return False

            # Absent: letter must not appear anywhere
            if any(letter in candidate for letter in absent_letters):
                return False

            # Yellow: letter must exist but NOT at this position
            for pos, letter in yellow.items():
                if candidate[pos] == letter or letter not in candidate:
                    return False

            # Excluded positions: confirmed letter must not be at grey position
            for letter, positions in excluded_at.items():
                if any(candidate[pos] == letter for pos in positions):
                    return False

            return True

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
        """
        Filter words based on multiple guesses and their feedback.

        Args:
            filter_spec: Dict mapping guessed words to their GuessFilter objects:
                {
                    "LEAST": GuessFilter(
                        green_positions=[2, 4],
                        yellow_positions=[],
                        grey_positions=[0, 1, 3]
                    )
                }
        """
        filtered = set(self.dictionary)

        for guess, feedback in filter_spec.items():
            filtered &= self._filter_characters(
                guess,
                yellow_positions=tuple(feedback.yellow_positions),
                green_positions=tuple(feedback.green_positions),
                grey_positions=tuple(feedback.grey_positions),
            )

        return sorted(filtered)


# Global instance
_wordle_helper = None


def get_wordle_helper(length: int = 5) -> WordleHelper:
    """Get or create WordleHelper instance"""
    global _wordle_helper
    if _wordle_helper is None:
        _wordle_helper = WordleHelper(length)
    return _wordle_helper
