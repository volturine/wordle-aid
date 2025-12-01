import logging
import os
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)


def get_database_path() -> Path:
    """Get the database path from the environment variable."""
    db_root_path = os.getenv('DB_ROOT_PATH')
    if not db_root_path:
        raise OSError('DB_ROOT_PATH environment variable is not set. Please set it to the root path of your database files.')
    return Path(db_root_path) / 'words.db'


def load_words_by_length(length: int) -> set[str]:
    """Load words of specified length from SQLite database.

    Args:
        length: The length of words to load

    Returns:
        Set of words of the specified length

    Raises:
        FileNotFoundError: If database doesn't exist
        sqlite3.Error: If database operation fails
    """
    logger.info(f'Loading dictionary for {length}-letter words from SQLite database')

    database_path = get_database_path()

    # Check if database exists
    if not database_path.exists():
        logger.error(f'Database not found at {database_path}')
        raise FileNotFoundError(f'Database not found at {database_path}. Please ensure DB_ROOT_PATH environment variable points to a valid database file.')  # noqa: E501

    # Load words from SQLite database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    try:
        # Get words of specified length
        cursor.execute('SELECT word FROM words WHERE length = ?', (length,))
        words = [row[0] for row in cursor.fetchall()]

        logger.info(f'Loaded {len(words)} words of length {length}')
        return set(words)

    except sqlite3.Error as e:
        logger.error(f'Database error while loading dictionary: {e}')
        raise
    finally:
        conn.close()
