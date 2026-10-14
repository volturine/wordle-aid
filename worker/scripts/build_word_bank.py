#!/usr/bin/env python3
"""Build the guess and likely-answer banks from the pinned source lists.

Reads database/sources, writes database/bank, and replaces the five-letter
rows in database/words.db. SQL export stays in export_db.py.
"""
import hashlib
import json
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / 'database' / 'sources'
BANK = ROOT / 'database' / 'bank'
WORDS_DB = ROOT / 'database' / 'words.db'

VERSION = '2026.10.14'
SOURCE_LABEL = 'tabatkins/wordle-list MIT + 12dicts 3of6game public domain'
SUPPLEMENT = (
    'detox',
    'geeky',
    'inbox',
    'latte',
    'penne',
    'pesto',
    'ramen',
    'rehab',
    'wimpy',
)
FORBIDDEN = ('aaron', 'abbie', 'abdom', 'accel', 'accts')


def five_letter_words(path: Path) -> set[str]:
    words: set[str] = set()
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        token = re.sub(r'[^A-Za-z].*$', '', line.split()[0]).lower()
        if re.fullmatch(r'[a-z]{5}', token):
            words.add(token)
    return words


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def main() -> None:
    guesses = five_letter_words(SOURCES / 'tabatkins-wordle-list.txt')
    common = five_letter_words(SOURCES / '12dicts-3of6game.txt')
    supplement = five_letter_words(SOURCES / 'answer-supplement.txt')
    if supplement != set(SUPPLEMENT):
        raise SystemExit(f'supplement drifted from the reviewed set: {sorted(supplement)}')
    missing = sorted(supplement - guesses)
    if missing:
        raise SystemExit(f'supplement words are not accepted guesses: {missing}')
    forbidden = sorted(set(FORBIDDEN) & guesses)
    if forbidden:
        raise SystemExit(f'guess list still contains excluded words: {forbidden}')

    answers = (common & guesses) | supplement
    BANK.mkdir(parents=True, exist_ok=True)
    (BANK / 'guesses.txt').write_text(''.join(f'{word}\n' for word in sorted(guesses)), encoding='utf-8')
    (BANK / 'answers.txt').write_text(''.join(f'{word}\n' for word in sorted(answers)), encoding='utf-8')
    metadata = {
        'version': VERSION,
        'source': SOURCE_LABEL,
        'guess_count': len(guesses),
        'answer_count': len(answers),
        'guess_sha256': sha256(BANK / 'guesses.txt'),
        'answer_sha256': sha256(BANK / 'answers.txt'),
        'inputs': {
            'tabatkins-wordle-list.txt': sha256(SOURCES / 'tabatkins-wordle-list.txt'),
            '12dicts-3of6game.txt': sha256(SOURCES / '12dicts-3of6game.txt'),
            'answer-supplement.txt': sha256(SOURCES / 'answer-supplement.txt'),
        },
    }
    (BANK / 'bank.json').write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')

    connection = sqlite3.connect(WORDS_DB)
    columns = {row[1] for row in connection.execute('PRAGMA table_info(words)')}
    if 'is_answer' not in columns:
        connection.execute('ALTER TABLE words ADD COLUMN is_answer INTEGER NOT NULL DEFAULT 0')
    connection.execute('DELETE FROM words WHERE length = 5')
    connection.executemany(
        'INSERT INTO words (word, length, is_answer) VALUES (?, 5, ?)',
        ((word, int(word in answers)) for word in sorted(guesses)),
    )
    connection.commit()
    connection.close()
    print(f'guesses {len(guesses)} answers {len(answers)} version {VERSION}')


if __name__ == '__main__':
    main()
