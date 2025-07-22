#!/usr/bin/env python3
"""
Migration script to convert words_alpha.txt to SQLite database
"""

import sqlite3
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

CURRENT_DIR = Path(__file__).parent
DATABASE_PATH = CURRENT_DIR / "words.db"
WORDS_FILE = CURRENT_DIR / "words_alpha.txt"


def create_database():
    """Create SQLite database with words table"""
    logger.info(f"Creating database at: {DATABASE_PATH}")

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Create words table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS words (
            word TEXT PRIMARY KEY,
            length INTEGER NOT NULL
        )
    """)

    # Create index on word for fast lookups
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_word ON words(word)")

    # Create index on length for filtering by word length
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_length ON words(length)")

    # Create composite index for length-based queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_length_word ON words(length, word)")

    conn.commit()
    conn.close()
    logger.info("Database schema created successfully")


def migrate_words():
    """Migrate words from text file to SQLite database"""
    logger.info(f"Reading words from: {WORDS_FILE}")

    if not WORDS_FILE.exists():
        logger.error(f"Words file not found: {WORDS_FILE}")
        return False

    # Read words from file
    with open(WORDS_FILE, "r") as file:
        words = file.read().strip().split()

    logger.info(f"Found {len(words)} words to migrate")

    # Insert words into database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Clear existing data
    cursor.execute("DELETE FROM words")

    # Prepare data for bulk insert
    word_data = [(word.lower(), len(word)) for word in words if word.strip()]

    try:
        cursor.executemany("INSERT OR IGNORE INTO words (word, length) VALUES (?, ?)", word_data)
        conn.commit()

        # Get count of inserted words
        cursor.execute("SELECT COUNT(*) FROM words")
        count = cursor.fetchone()[0]
        logger.info(f"Successfully migrated {count} words to database")

        # Show some statistics
        cursor.execute("SELECT length, COUNT(*) FROM words GROUP BY length ORDER BY length")
        stats = cursor.fetchall()
        logger.info("Word length statistics:")
        for length, count in stats[:10]:  # Show first 10 lengths
            logger.info(f"  Length {length}: {count} words")

    except sqlite3.Error as e:
        logger.error(f"Error during migration: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

    return True


def verify_migration():
    """Verify the migration was successful"""
    logger.info("Verifying migration...")

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Check total word count
    cursor.execute("SELECT COUNT(*) FROM words")
    total_count = cursor.fetchone()[0]
    logger.info(f"Total words in database: {total_count}")

    # Check 5-letter words (most common for Wordle)
    cursor.execute("SELECT COUNT(*) FROM words WHERE length = 5")
    five_letter_count = cursor.fetchone()[0]
    logger.info(f"5-letter words: {five_letter_count}")

    # Show some sample words
    cursor.execute("SELECT word FROM words WHERE length = 5 ORDER BY word LIMIT 10")
    sample_words = [row[0] for row in cursor.fetchall()]
    logger.info(f"Sample 5-letter words: {', '.join(sample_words)}")

    conn.close()
    logger.info("Migration verification complete")


if __name__ == "__main__":
    logger.info("Starting words migration to SQLite")

    try:
        create_database()
        if migrate_words():
            verify_migration()
            logger.info("Migration completed successfully!")
        else:
            logger.error("Migration failed!")
    except Exception as e:
        logger.error(f"Migration error: {e}")
