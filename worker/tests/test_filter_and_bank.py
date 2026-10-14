import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'worker' / 'src'))

from bank_contract import FORBIDDEN_GUESSES, REQUIRED_ANSWERS, bank_problem
from filter_service import WordleHelper
from memory_cache import InFlight, LruCache, TtlCache, classify_definition
from request_validation import parse_constraints, parse_page


def helper(words, answers=None):
    answer_set = set(words) if answers is None else set(answers)
    return WordleHelper(set(words), answer_set, 5, 'test')


def constraint(guess, green=(), yellow=(), gray=()):
    return {
        'guess': guess,
        'correct_position': list(green),
        'incorrect_position': list(yellow),
        'incorrect_letter': list(gray),
    }


def score(answer: str, guess: str):
    """Two-pass Wordle score: greens consume letters before yellows."""
    colors = ['gray'] * 5
    remaining = list(answer)
    for index, letter in enumerate(guess):
        if answer[index] == letter:
            colors[index] = 'green'
            remaining[index] = None
    for index, letter in enumerate(guess):
        if colors[index] == 'green':
            continue
        if letter in remaining:
            colors[index] = 'yellow'
            remaining[remaining.index(letter)] = None
    return (
        [index for index, color in enumerate(colors) if color == 'green'],
        [index for index, color in enumerate(colors) if color == 'yellow'],
        [index for index, color in enumerate(colors) if color == 'gray'],
    )


class FilterTests(unittest.TestCase):
    def test_duplicate_letter_gray_means_exact_count(self):
        words = helper(['ether', 'exite', 'other', 'exact'])
        result = words._filter_characters('ether', (1,), (0,), (2, 3, 4))
        self.assertIn('exact', result)
        self.assertNotIn('exite', result)
        self.assertNotIn('other', result)

    def test_repeated_guess_rows_both_apply(self):
        words = helper(['coral', 'moral', 'crane', 'crank'], answers={'coral'})
        page = words.filter_page(
            [
                constraint('crane', green=(0,)),
                constraint('crane', yellow=(1,)),
            ],
            limit=100,
            answer_offset=0,
            guess_offset=0,
        )
        self.assertEqual(page['answers'], ['coral'])
        self.assertEqual(page['guesses'], [])
        self.assertEqual(page['answer_total'], 1)
        self.assertFalse(page['needs_clue'])

    def test_partial_clue_keeps_unknown_squares(self):
        words = helper(['crane', 'crate', 'crank', 'prank'])
        result = words._filter_characters('c____', (), (0,), ())
        self.assertEqual(result, {'crane', 'crate', 'crank'})

    def test_empty_clue_does_not_return_the_bank(self):
        words = helper(['crane', 'slate'])
        page = words.filter_page([], limit=100, answer_offset=0, guess_offset=0)
        self.assertEqual(page['answers'], [])
        self.assertEqual(page['guesses'], [])
        self.assertTrue(page['needs_clue'])

    def test_pages_are_bounded_and_split_by_answer_set(self):
        words = helper(['crane', 'crate', 'crank', 'slate'], answers={'crane', 'slate'})
        page = words.filter_page([constraint('crane', green=(0,))], limit=1, answer_offset=0, guess_offset=1)
        self.assertEqual(page['answers'], ['crane'])
        self.assertEqual(page['answer_total'], 1)
        self.assertEqual(page['guesses'], ['crate'])
        self.assertEqual(page['guess_total'], 2)

    def test_scored_guess_still_contains_its_answer(self):
        bank = ['apple', 'puppy', 'eerie', 'elder', 'books', 'boost', 'alert', 'alter']
        words = helper(bank)
        for answer, guess in (
            ('alert', 'alter'),
            ('apple', 'puppy'),
            ('eerie', 'elder'),
            ('books', 'boost'),
            ('apple', 'apple'),
        ):
            green, yellow, gray = score(answer, guess)
            result = words._filter_characters(guess, tuple(yellow), tuple(green), tuple(gray))
            self.assertIn(answer, result, f'{guess} -> {answer}')

    def test_unknown_green_letter_is_empty_rather_than_an_error(self):
        words = helper(['crane'])
        self.assertEqual(words._filter_characters('qqqqq', (), (0,), ()), set())


class ValidationTests(unittest.TestCase):
    def test_preserves_duplicate_guess_rows_and_partial_patterns(self):
        constraints = parse_constraints({
            'constraints': [
                {'guess': 'CRANE', 'correct_position': [0], 'incorrect_position': [], 'incorrect_letter': [1, 2, 3, 4]},
                {'guess': 'c_a__', 'correct_position': [0, 2], 'incorrect_position': [], 'incorrect_letter': []},
            ]
        })
        self.assertEqual(len(constraints), 2)
        self.assertEqual(constraints[0]['guess'], 'crane')
        self.assertEqual(constraints[1]['guess'], 'c_a__')

    def test_rejects_malformed_feedback(self):
        bodies = [
            {'constraints': [{'guess': 'crane', 'correct_position': None}]},
            {'constraints': [{'guess': 'crane', 'correct_position': [99]}]},
            {'constraints': [{'guess': 'crane', 'correct_position': [-1]}]},
            {'constraints': [{'guess': 'crane', 'correct_position': [True]}]},
            {'constraints': [{'guess': 'crane', 'correct_position': [0], 'incorrect_letter': [0]}]},
            {'constraints': [{'guess': 'c____', 'correct_position': [1]}]},
            {'constraints': [{'guess': 'crane'}] * 7},
            {'filter_spec': {}},
        ]
        for body in bodies:
            with self.assertRaises(ValueError):
                parse_constraints(body)

    def test_page_bounds(self):
        self.assertEqual(parse_page({'constraints': []}), (100, 0, 0))
        with self.assertRaises(ValueError):
            parse_page({'constraints': [], 'limit': 0})
        with self.assertRaises(ValueError):
            parse_page({'constraints': [], 'answer_offset': -1})


class BankTests(unittest.TestCase):
    def test_shipped_bank_matches_the_contract(self):
        guesses = set((ROOT / 'database' / 'bank' / 'guesses.txt').read_text().split())
        answers = set((ROOT / 'database' / 'bank' / 'answers.txt').read_text().split())
        meta = json.loads((ROOT / 'database' / 'bank' / 'bank.json').read_text())
        self.assertIsNone(bank_problem(guesses, answers, meta['guess_count'], meta['answer_count']))
        self.assertTrue(set(REQUIRED_ANSWERS) <= answers)
        self.assertFalse(set(FORBIDDEN_GUESSES) & guesses)
        replacement = (ROOT / 'worker' / 'migrations' / 'replace_dictionary.sql').read_text()
        self.assertIn('DELETE FROM words;', replacement)
        self.assertIn("VALUES ('latte', 5, 1);", replacement)
        self.assertNotIn('into definitions', replacement.lower())
        self.assertNotIn('from definitions', replacement.lower())
        self.assertNotIn("'accts'", replacement)

    def test_empty_bank_is_not_ready(self):
        self.assertIsNotNone(bank_problem(set(), set(), 0, 0))


class CacheTests(unittest.TestCase):
    def test_lru_and_ttl_evict(self):
        lru = LruCache(2)
        lru.set('a', {'definitions': [1]})
        lru.set('b', {'definitions': []})
        lru.get('a')
        lru.set('c', {'definitions': [2]})
        self.assertIsNone(lru.get('b'))
        self.assertIsNotNone(lru.get('a'))

        ttl = TtlCache(2, ttl_seconds=10)
        ttl.set('miss', True, now=0)
        self.assertTrue(ttl.get('miss', now=9))
        self.assertIsNone(ttl.get('miss', now=10))
        ttl.set('one', True, now=0)
        ttl.set('two', True, now=0)
        ttl.set('three', True, now=0)
        self.assertIsNone(ttl.get('one', now=0))

    def test_definition_classification(self):
        self.assertEqual(classify_definition(404, None), 'missing')
        self.assertEqual(classify_definition(200, {'definitions': []}), 'ready')
        self.assertEqual(classify_definition(200, {'word': 'crane'}), 'error')
        self.assertEqual(classify_definition(500, {'definitions': []}), 'error')

    def test_inflight_shares_one_lookup(self):
        import asyncio

        async def scenario():
            flight = InFlight()
            first, leader = flight.start('crane')
            second, other = flight.start('crane')
            self.assertTrue(leader)
            self.assertFalse(other)
            flight.succeed('crane', {'definitions': []})
            return await first, await second

        self.assertEqual(asyncio.run(scenario()), ({'definitions': []}, {'definitions': []}))

    def test_unfollowed_failure_is_observed(self):
        import asyncio
        import gc

        async def scenario():
            flight = InFlight()
            future, leader = flight.start('gone')
            self.assertTrue(leader)
            flight.fail('gone', RuntimeError('down'))
            self.assertFalse(future._log_traceback)
            del future
            gc.collect()
            await asyncio.sleep(0)

        loop = asyncio.new_event_loop()
        reports = []
        loop.set_exception_handler(lambda _loop, context: reports.append(context.get('message', '')))
        try:
            loop.run_until_complete(scenario())
        finally:
            loop.close()
        self.assertEqual(reports, [])

    def test_followers_still_receive_the_failure(self):
        import asyncio

        async def scenario():
            flight = InFlight()
            _leader, leader = flight.start('gone')
            follower, other = flight.start('gone')
            self.assertTrue(leader)
            self.assertFalse(other)
            flight.fail('gone', RuntimeError('down'))
            with self.assertRaisesRegex(RuntimeError, 'down'):
                await follower

        asyncio.run(scenario())


if __name__ == '__main__':
    unittest.main()
