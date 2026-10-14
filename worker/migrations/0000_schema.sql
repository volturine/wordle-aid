-- Wordle Aid schema (no dictionary rows — those come from replace_dictionary.sql)
CREATE TABLE IF NOT EXISTS words (
  word TEXT PRIMARY KEY,
  length INTEGER NOT NULL,
  is_answer INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_words_length ON words (length, word);
CREATE TABLE IF NOT EXISTS definitions (
  word TEXT PRIMARY KEY,
  definition_data TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS bank_meta (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  version TEXT NOT NULL,
  guess_count INTEGER NOT NULL,
  answer_count INTEGER NOT NULL,
  source TEXT NOT NULL
);
