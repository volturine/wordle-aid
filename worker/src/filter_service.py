"""Wordle word filtering service (migrated from backend/modules/filter)."""
import logging
from collections import Counter
from functools import lru_cache

from bank_contract import bank_problem
from db import d1_all, d1_first

logger = logging.getLogger(__name__)


class DictionaryNotReady(Exception):
    """The isolate does not have a usable guess and answer bank."""


class WordleHelper:
    def __init__(self, dictionary: set[str], answers: set[str], length: int = 5, version: str = ''):
        logger.info(
            f'Initializing WordleHelper for {length}-letter words '
            f'({len(dictionary)} guesses, {len(answers)} likely answers)'
        )
        self.length = length
        self.dictionary = dictionary
        self.answers = answers
        self.version = version

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
            pools = []
            for pos, letter in green.items():
                positions = self.processed_dictionary.get(letter)
                if not positions:
                    return set()
                pools.append(positions[pos])
            candidates = set.intersection(*pools)
        else:
            candidates = self.dictionary

        return {word for word in candidates if matches(word)}

    def filter_page(self, constraints: list[dict], limit: int, offset: int) -> dict:
        """Return one page of every matching word."""
        page = {
            'words': [],
            'total': 0,
            'offset': offset,
            'limit': limit,
            'needs_clue': not constraints,
            'bank_version': self.version,
        }
        if not constraints:
            return page

        filtered = set(self.dictionary)
        for constraint in constraints:
            filtered &= self._filter_characters(
                constraint['guess'],
                incorrect_position=tuple(constraint['incorrect_position']),
                correct_position=tuple(constraint['correct_position']),
                incorrect_letter=tuple(constraint['incorrect_letter']),
            )

        words = sorted(filtered)
        page['words'] = words[offset:offset + limit]
        page['total'] = len(words)
        return page


# Per-isolate cache: length -> (bank version, helper). A new bank version reloads.
_wordle_helpers: dict[int, tuple[str, WordleHelper]] = {}


async def get_wordle_helper(env, length: int = 5) -> WordleHelper:
    """Load the reviewed bank, refusing an empty or stale dictionary."""
    meta = await d1_first(
        env.DB,
        'SELECT version, guess_count, answer_count FROM bank_meta WHERE id = 1',
    )
    if not isinstance(meta, dict) or not meta.get('version'):
        raise DictionaryNotReady('missing bank metadata')
    version = str(meta['version'])
    cached = _wordle_helpers.get(length)
    if cached and cached[0] == version:
        return cached[1]

    logger.info(f'Loading dictionary for {length}-letter words from D1')
    rows = await d1_all(env.DB, 'SELECT word, is_answer FROM words WHERE length = ?', length)
    words: set[str] = set()
    answers: set[str] = set()
    for row in rows:
        word = str(row['word']).lower()
        words.add(word)
        if row.get('is_answer'):
            answers.add(word)
    problem = bank_problem(words, answers, int(meta['guess_count']), int(meta['answer_count']))
    if problem:
        raise DictionaryNotReady(problem)
    helper = WordleHelper(words, answers, length, version)
    _wordle_helpers[length] = (version, helper)
    return helper
