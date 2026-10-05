-- Wordle Aid schema (no data — data imports are one-time/managed separately)
CREATE TABLE IF NOT EXISTS words (
  word TEXT PRIMARY KEY,
  length INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_words_length ON words (length, word);
CREATE TABLE IF NOT EXISTS definitions (
  word TEXT PRIMARY KEY,
  definition_data TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
