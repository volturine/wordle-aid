"""
Database models and operations for word filtering
"""

import os
import sqlite3
import logging
from pathlib import Path

# Get database path from environment variable
DB_ROOT_PATH = os.getenv("DB_ROOT_PATH")
if not DB_ROOT_PATH:
    raise EnvironmentError("DB_ROOT_PATH environment variable is not set. Please set it to the root path of your database files.")

DATABASE_PATH = Path(DB_ROOT_PATH) / "words.db"

logger = logging.getLogger(__name__)


def load_words_by_length(length: int) -> set[str]:
    """
    Load words of specified length from SQLite database

    Args:
        length: The length of words to load

    Returns:
        Set of words of the specified length

    Raises:
        FileNotFoundError: If database doesn't exist
        sqlite3.Error: If database operation fails
    """
    logger.info(f"Loading dictionary for {length}-letter words from SQLite database")

    # Check if database exists
    if not DATABASE_PATH.exists():
        logger.error(f"Database not found at {DATABASE_PATH}")
        raise FileNotFoundError(f"Database not found at {DATABASE_PATH}. Please ensure DB_ROOT_PATH environment variable points to a valid database file.")

    # Load words from SQLite database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # Get words of specified length
        cursor.execute(f"SELECT word FROM words WHERE length = {length}")
        words = [row[0] for row in cursor.fetchall()]

        logger.info(f"Loaded {len(words)} words of length {length}")
        return set(words)

    except sqlite3.Error as e:
        logger.error(f"Database error while loading dictionary: {e}")
        raise
    finally:
        conn.close()
