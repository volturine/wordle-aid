"""
Database models for word definitions
"""

import os
import sqlite3
import json
import logging
from pathlib import Path

# Get database path from environment variable
DB_ROOT_PATH = os.getenv("DB_ROOT_PATH")
if not DB_ROOT_PATH:
    raise EnvironmentError("DB_ROOT_PATH environment variable is not set. Please set it to the root path of your database files.")

WORD_DEFINITIONS_DB_PATH = Path(DB_ROOT_PATH) / "word_definitions.db"

logger = logging.getLogger(__name__)


def init_db():
    """Initialize the word definitions database"""
    conn = sqlite3.connect(WORD_DEFINITIONS_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS definitions (
            word TEXT PRIMARY KEY,
            definition_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def get_cached_definition(word: str):
    """Get definition from SQLite cache"""
    try:
        conn = sqlite3.connect(WORD_DEFINITIONS_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT definition_data FROM definitions WHERE word = ?", (word.lower(),))
        result = cursor.fetchone()
        conn.close()

        if result:
            return json.loads(result[0])
        return None
    except Exception as e:
        logger.error(f"Error reading from cache for '{word}': {e}")
        return None


def store_definition(word: str, definition_data: dict):
    """Store definition in SQLite cache"""
    try:
        conn = sqlite3.connect(WORD_DEFINITIONS_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO definitions (word, definition_data) VALUES (?, ?)", (word.lower(), json.dumps(definition_data)))
        conn.commit()
        conn.close()
        logger.info(f"Cached definition for word: {word}")
    except Exception as e:
        logger.error(f"Error caching definition for '{word}': {e}")
