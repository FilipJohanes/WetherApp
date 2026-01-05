#!/usr/bin/env python3
"""Initialize database with correct new schema."""

import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db_schema():
    """Initialize database schema with all tables."""
    conn = sqlite3.connect("app.db")
    conn.execute("PRAGMA foreign_keys = ON")
    
    try:
        # Create users table (simplified, no lat/lon here)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                weather_enabled INTEGER DEFAULT 0,
                reminder_enabled INTEGER DEFAULT 0,
                language TEXT DEFAULT 'en'
            )
        """)
        logger.info("Users table created/verified")
        
        # Create weather_subscriptions table (this has lat/lon)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS weather_subscriptions (
                email TEXT PRIMARY KEY,
                location TEXT NOT NULL,
                lat REAL NOT NULL,
                lon REAL NOT NULL,
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE
            )
        """)
        logger.info("Weather subscriptions table created/verified")
        
        # Create countdowns table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS countdowns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                event_name TEXT NOT NULL,
                event_date TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE
            )
        """)
        logger.info("Countdowns table created/verified")
        
        # Create password_reset_tokens table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                token TEXT PRIMARY KEY,
                email TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                expires_at TEXT NOT NULL,
                used INTEGER DEFAULT 0,
                FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE
            )
        """)
        logger.info("Password reset tokens table created/verified")
        
        conn.commit()
        logger.info("Database schema updated successfully")
        
    finally:
        conn.close()

if __name__ == "__main__":
    init_db_schema()
    print("✅ Database initialized with correct schema!")