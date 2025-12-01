import sqlite3

import pytest

from modules.filter.service import WordleHelper


# Define a fixture to create a temporary database
@pytest.fixture
def test_db(tmp_path, monkeypatch):
    # Create a temporary directory for the database
    db_dir = tmp_path / 'database'
    db_dir.mkdir()

    # Create the database file
    db_path = db_dir / 'words.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table
    cursor.execute('CREATE TABLE words (word TEXT PRIMARY KEY, length INTEGER)')

    # Insert test data
    # We include words needed for all tests
    test_words = [
        ('ether', 5),
        ('exite', 5),
        ('exact', 5),
        ('other', 5),
        ('apple', 5),
        ('alert', 5),
        ('alter', 5),
        ('baker', 5),
        ('cider', 5),
        ('start', 5),
        ('tarts', 5),
        ('stare', 5),
    ]
    cursor.executemany('INSERT INTO words (word, length) VALUES (?, ?)', test_words)

    conn.commit()
    conn.close()

    # Set the DB_ROOT_PATH environment variable to the temp dir
    # This ensures load_words_by_length uses our test database instead of the real one
    monkeypatch.setenv('DB_ROOT_PATH', str(db_dir))

    yield db_dir


def test_filter_ether_case(test_db):
    """Test the specific case where a letter appears multiple times in a guess.

    One instance is confirmed (Green/Yellow) while another is Grey.
    This implies an exact count of that letter.
    """
    # Initialize helper (will load from test_db)
    helper = WordleHelper(length=5)

    # Guess: "ether"
    # 0: 'e' (Green)
    # 1: 't' (Yellow)
    # 2: 'h' (Grey)
    # 3: 'e' (Grey) -> Crucial: implies exactly one 'e' in target
    # 4: 'r' (Grey)

    guess = 'ether'
    correct_position = (0,)  # e at 0
    incorrect_position = (1,)  # t at 1
    incorrect_letter = (2, 3, 4)  # h, e, r

    result = helper._filter_characters(guess, incorrect_position, correct_position, incorrect_letter)

    # "exite" has 'e' at 0 and 'e' at 4. Two 'e's. Should be rejected.
    assert 'exite' not in result, "'exite' should be rejected because it has two 'e's"

    # "other" has 'h' and 'r'. Should be rejected.
    assert 'other' not in result, "'other' should be rejected because it contains 'h' and 'r'"

    # "exact"
    # e at 0 (Match Green)
    # x at 1 (Not 't', so 't' is not at 1. Good)
    # a at 2
    # c at 3
    # t at 4 (Contains 't'. Good)
    # No 'h', 'r'.
    # Exactly one 'e'.
    assert 'exact' in result, "'exact' should be accepted"


def test_basic_filtering(test_db):
    helper = WordleHelper(length=5)

    # Guess: "alter"
    # Target: "alert"
    # a (0) -> Green
    # l (1) -> Green
    # t (2) -> Yellow (is in word, but not at 2)
    # e (3) -> Yellow (is in word, but not at 3)
    # r (4) -> Yellow (is in word, but not at 4)

    guess = 'alter'
    correct_position = (0, 1)  # a, l
    incorrect_position = (2, 3, 4)  # t, e, r
    incorrect_letter = ()

    result = helper._filter_characters(guess, incorrect_position, correct_position, incorrect_letter)

    assert 'alert' in result
    assert 'apple' not in result  # Missing t, e, r
    assert 'baker' not in result  # Missing a, l...


def test_grey_letters_exclude_words(test_db):
    helper = WordleHelper(length=5)

    # Guess: "apple"
    # All grey (none in target)
    guess = 'apple'
    correct_position = ()
    incorrect_position = ()
    incorrect_letter = (0, 1, 2, 3, 4)  # a, p, p, l, e

    result = helper._filter_characters(guess, incorrect_position, correct_position, incorrect_letter)

    assert 'apple' not in result
    assert 'baker' not in result  # Contains 'a', 'e'
    assert 'cider' not in result  # Contains 'e'

    # If we had a word with none of those letters
    # e.g. "ghost" (if in dict)
    # But our mock dict is small. Result should be empty here.
    assert len(result) == 0


def test_yellow_position_constraint(test_db):
    helper = WordleHelper(length=5)

    # Guess: "stare"
    # s (0) -> Yellow (in word, not at 0)
    # t (1) -> Yellow (in word, not at 1)
    # a (2) -> Yellow (in word, not at 2)
    # r (3) -> Yellow (in word, not at 3)
    # e (4) -> Yellow (in word, not at 4)
    # Target could be "tarts" (t,a,r,t,s) - wait, 'e' is missing.

    # Let's try a simpler one.
    # Guess: "ab..."
    # a at 0 is Yellow.
    # Means 'a' is in word, but NOT at 0.

    guess = 'abcde'
    correct_position = ()
    incorrect_position = (0,)  # a is yellow
    incorrect_letter = (1, 2, 3, 4)  # b, c, d, e grey

    # "apple" (a at 0) -> Should fail because a is at 0.
    # "baker" (a at 1) -> Should pass (contains a, not at 0, no b,c,d,e... wait b,e are grey)
    # "baker" has b(0), a(1), k(2), e(3), r(4).
    # b is grey -> fail.

    # Let's use "tarts" vs "start"
    # Guess "start"
    # s(0) Yellow -> s in word, not at 0.
    # "tarts" has s at 4. OK.

    guess = 'start'
    correct_position = ()
    incorrect_position = (0,)  # s is yellow
    incorrect_letter = ()  # ignore others for this test

    result = helper._filter_characters(guess, incorrect_position, correct_position, incorrect_letter)

    assert 'start' not in result  # s is at 0
    assert 'tarts' in result  # s is at 4
