#!/usr/bin/env python3
"""Export local SQLite DBs to SQL files for D1.

Usage:
    python scripts/export_db.py [--lengths 5]
    python scripts/export_db.py --definitions

Reads database/words.db and database/bank/bank.json. Writes
migrations/0001_words.sql (insert-only, for an empty database) and
migrations/replace_dictionary.sql (deletes dictionary rows, then inserts
the current bank). Definitions are exported only with --definitions, and
that file never updates a row that already exists.
"""
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DB_DIR = ROOT / 'database'
OUT = ROOT / 'worker' / 'migrations'

args = sys.argv
LENGTHS = [int(x) for x in args[args.index('--lengths') + 1:]] if '--lengths' in args else [5]
EXPORT_DEFINITIONS = '--definitions' in args

OUT.mkdir(parents=True, exist_ok=True)

bank = json.loads((DB_DIR / 'bank' / 'bank.json').read_text(encoding='utf-8'))
connection = sqlite3.connect(DB_DIR / 'words.db')
words = connection.execute(
    f'SELECT word, is_answer FROM words WHERE length IN ({",".join("?" * len(LENGTHS))}) ORDER BY word',
    LENGTHS,
).fetchall()
connection.close()

for word, _is_answer in words:
    if not word.isalpha() or not word.islower():
        raise SystemExit(f'refusing to export unsafe word {word!r}')
answer_rows = sum(int(is_answer) for _word, is_answer in words)
if len(words) != bank['guess_count'] or answer_rows != bank['answer_count']:
    raise SystemExit(
        f"sqlite five-letter rows ({len(words)} guesses, {answer_rows} answers) "
        f"do not match bank.json ({bank['guess_count']}, {bank['answer_count']})"
    )

schema = (
    '-- Accepted guesses and likely answers for Wordle Aid\n'
    'CREATE TABLE IF NOT EXISTS words (\n'
    '  word TEXT PRIMARY KEY,\n'
    '  length INTEGER NOT NULL,\n'
    '  is_answer INTEGER NOT NULL DEFAULT 0\n'
    ');\n'
    'CREATE INDEX IF NOT EXISTS idx_words_length ON words (length, word);\n'
)
# No BEGIN/COMMIT: D1 rejects explicit transactions in --file imports.
fresh_path = OUT / '0001_words.sql'
replace_path = OUT / 'replace_dictionary.sql'
with fresh_path.open('w', encoding='utf-8') as handle:
    handle.write(schema)
    handle.write('-- Insert-only. Re-importing does not update or remove rows.\n')
    for word, is_answer in words:
        handle.write(
            'INSERT INTO words (word, length, is_answer) '
            f"VALUES ('{word}', {len(word)}, {int(is_answer)}) ON CONFLICT (word) DO NOTHING;\n"
        )

source = bank['source'].replace("'", "''")
with replace_path.open('w', encoding='utf-8') as handle:
    handle.write('-- Replaces the dictionary. Does not read or write the definitions table.\n')
    handle.write('DELETE FROM words;\n')
    for word, is_answer in words:
        handle.write(
            'INSERT INTO words (word, length, is_answer) '
            f"VALUES ('{word}', {len(word)}, {int(is_answer)});\n"
        )
    handle.write(
        'INSERT INTO bank_meta (id, version, guess_count, answer_count, source) '
        f"VALUES (1, '{bank['version']}', {bank['guess_count']}, {bank['answer_count']}, '{source}')\n"
        'ON CONFLICT (id) DO UPDATE SET\n'
        '  version = excluded.version,\n'
        '  guess_count = excluded.guess_count,\n'
        '  answer_count = excluded.answer_count,\n'
        '  source = excluded.source;\n'
    )

print(f'Wrote {len(words)} words -> {fresh_path.name} and {replace_path.name}')

if not EXPORT_DEFINITIONS:
    raise SystemExit(0)

# --- definitions ---
conn = sqlite3.connect(DB_DIR / 'word_definitions.db')
rows = conn.execute('SELECT word, definition_data FROM definitions').fetchall()
conn.close()

defs_path = OUT / '0002_definitions.sql'
with open(defs_path, 'w') as f:
    f.write('-- Cached word definitions\n')
    f.write(
        'CREATE TABLE IF NOT EXISTS definitions (\n'
        '  word TEXT PRIMARY KEY,\n'
        '  definition_data TEXT NOT NULL,\n'
        '  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n'
        ');\n'
    )
    for word, data in rows:
        # definition_data is already a JSON string; only escape single quotes for the SQL literal
        escaped = data.replace("'", "''")
        f.write(f"INSERT INTO definitions (word, definition_data) VALUES ('{word}', '{escaped}') ON CONFLICT (word) DO NOTHING;\n")

print(f'Wrote {len(rows)} definitions -> {defs_path.name}')
