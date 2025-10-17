"""
Database models and operations for word filtering
"""

import os
import sqlite3
import logging
from pathlib import Path

# Get database path from environment variable
DATABASE_PATH_STR = os.getenv("WORDS_DB_PATH")
if not DATABASE_PATH_STR:
    raise EnvironmentError("WORDS_DB_PATH environment variable is not set. Please set it to the path of your words.db file.")

DATABASE_PATH = Path(DATABASE_PATH_STR) / "words.db"

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
        raise FileNotFoundError(f"Database not found at {DATABASE_PATH}. Please ensure WORDS_DB_PATH environment variable points to a valid database file.")

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
