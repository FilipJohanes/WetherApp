#!/usr/bin/env python3
"""Initialize database with language column."""

import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db_schema():
    """Initialize database schema with language support."""
    conn = sqlite3.connect("app.db")
    try:
        # Create subscribers table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS subscribers (
                email TEXT PRIMARY KEY,
                location TEXT NOT NULL,
                lat REAL NULL,
                lon REAL NULL,
                updated_at TEXT NOT NULL,
                personality TEXT DEFAULT 'neutral',
                language TEXT DEFAULT 'en'
            )
        """)
        
        # Add personality column if missing (backward compatibility)
        try:
            conn.execute("ALTER TABLE subscribers ADD COLUMN personality TEXT DEFAULT 'neutral'")
            logger.info("Added personality column to subscribers table")
        except sqlite3.OperationalError:
            pass
        
        # Add language column if missing
        try:
            conn.execute("ALTER TABLE subscribers ADD COLUMN language TEXT DEFAULT 'en'")
            logger.info("Added language column to subscribers table")
        except sqlite3.OperationalError:
            pass
        
        conn.commit()
        logger.info("Database schema updated successfully")
        
    finally:
        conn.close()

if __name__ == "__main__":
    init_db_schema()
    print("✅ Database initialized with language support!")