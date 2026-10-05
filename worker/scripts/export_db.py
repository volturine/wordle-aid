#!/usr/bin/env python3
"""Export local SQLite DBs to SQL files for D1 migrations.

Usage:
    python scripts/export_db.py [--lengths 5 6]

Reads from ../database/words.db and ../database/word_definitions.db,
writing migrations/0001_words.sql and 0002_definitions.sql.
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

OUT.mkdir(parents=True, exist_ok=True)

# --- words ---
conn = sqlite3.connect(DB_DIR / 'words.db')
words = conn.execute(
    f'SELECT word FROM words WHERE length IN ({",".join("?" * len(LENGTHS))})',
    LENGTHS,
).fetchall()
conn.close()

words_path = OUT / '0001_words.sql'
with open(words_path, 'w') as f:
    f.write('-- Dictionary words for Wordle Aid\n')
    f.write('CREATE TABLE IF NOT EXISTS words (\n  word TEXT PRIMARY KEY,\n  length INTEGER NOT NULL\n);\n')
    f.write('CREATE INDEX IF NOT EXISTS idx_words_length ON words (length, word);\n')
    f.write('BEGIN TRANSACTION;\n')
    f.write('DELETE FROM words;\n')
    for (word,) in words:
        f.write(f"INSERT INTO words (word, length) VALUES ('{word}', {len(word)});\n")
    f.write('COMMIT;\n')
print(f'Wrote {len(words)} words -> {words_path.name}')

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
    f.write('BEGIN TRANSACTION;\n')
    for word, data in rows:
        # definition_data is already a JSON string; only escape single quotes for the SQL literal
        escaped = data.replace("'", "''")
        f.write(f"INSERT INTO definitions (word, definition_data) VALUES ('{word}', '{escaped}');\n")
    f.write('COMMIT;\n')
print(f'Wrote {len(rows)} definitions -> {defs_path.name}')
