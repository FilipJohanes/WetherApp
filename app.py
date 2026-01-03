#!/usr/bin/env python3
"""
Daily Brief Service - Email-driven weather subscriptions.
Copyright (c) 2025 Filip Johanes. All Rights Reserved.

PROPRIETARY SOFTWARE - DO NOT DISTRIBUTE
This software contains proprietary algorithms and unique features including
Slovak "emuska" personality mode. Commercial use or redistribution prohibited.

This service monitors an email inbox for commands and provides:
1. Daily weather digest subscriptions (send location to subscribe)
2. Multi-language support (EN/ES/SK) and personality modes
3. Smart email parsing with system email filtering

Features:
- Weather forecasts at 05:00 local time
- 4 personality modes: neutral, cute, brutal, emuska
- Unicode-safe logging for international users
- Webhook architecture for scalability

Requirements:
- Python 3.11+
- See requirements.txt for dependencies
- Environment variables for email configuration
"""

import os
import sqlite3
import sys
import logging
import signal
import argparse
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from services.weather_service import list_subscribers
from services.email_service import start_email_monitor, stop_email_monitor, send_test_email, run_daily_job
from services.reminder_service import list_reminders, run_due_reminders_job
from timezonefinder import TimezoneFinder

# Global scheduler variable for signal handling
scheduler = None

# Initialize timezone finder (reused across all lookups)
tf = TimezoneFinder()

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv is optional, environment variables can be set manually
    pass

# Configure logging with UTF-8 encoding to handle emojis
from services.logging_service import logger

def signal_handler(signum, frame):
    """Graceful shutdown handler for Ctrl+C and other signals"""
    signal_names = {
        signal.SIGINT: "SIGINT (Ctrl+C)",
        signal.SIGTERM: "SIGTERM"
    }
    signal_name = signal_names.get(signum, f"Signal {signum}")
    
    logger.info(f"🛑 Received {signal_name} - Shutting down Daily Brief Service gracefully...")
    
    stop_email_monitor()
    
    if scheduler and scheduler.running:
        logger.info("⏰ Stopping scheduled jobs...")
        scheduler.shutdown(wait=False)
        logger.info("✅ Daily Brief Service stopped successfully")
    else:
        logger.info("⚠️ Scheduler not running")
    
    print("\n👋 Daily Brief Service has been stopped. Goodbye!")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # Termination signal


class Config:
    """Configuration from environment variables."""
    def __init__(self):
        self.email_address = self._get_env("EMAIL_ADDRESS")
        self.email_password = self._get_env("EMAIL_PASSWORD")
        self.imap_host = self._get_env("IMAP_HOST")
        self.imap_port = int(os.getenv("IMAP_PORT", "993"))
        self.smtp_host = self._get_env("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        self.timezone = os.getenv("TZ", "Europe/Bratislava")
        self.language = os.getenv("LANGUAGE", "en")  # Default to English
        
    def _get_env(self, key: str) -> str:
        """Get required environment variable or exit."""
        value = os.getenv(key)
        if not value:
            logger.error(f"Required environment variable {key} is not set")
            sys.exit(1)
        return value


def load_env() -> Config:
    """Load and validate environment configuration."""
    logger.info("Loading configuration from environment variables")
    # Check which .env file is being used
    env_path = os.path.abspath('.env')
    if os.path.exists(env_path):
        logger.info(f"✅ Using .env file: {env_path}")
    else:
        logger.info("⚠️ No .env file found - using system environment variables")

    config = Config()

    # Log the loaded EMAIL_PASSWORD for verification (masking for safety)
    pw_display = config.email_password[:2] + "***" + config.email_password[-2:] if config.email_password and len(config.email_password) > 4 else "***"
    logger.info(f"Loaded EMAIL_PASSWORD: {pw_display}")

    # Set timezone globally
    os.environ['TZ'] = config.timezone

    logger.info(f"Configuration loaded - Email: {config.email_address}, TZ: {config.timezone}")
    return config


def init_db(path: str = None) -> None:
    """Initialize SQLite database with unified schema."""
    if path is None:
        path = os.getenv("APP_DB_PATH", "app.db")
    logger.info(f"Initializing database at {path}")
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")
    
    try:
        # Master users table - central user registry
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                username TEXT,
                nickname TEXT,
                password_hash TEXT,
                timezone TEXT DEFAULT 'UTC',
                lat REAL,
                lon REAL,
                subscription_type TEXT DEFAULT 'free',
                weather_enabled INTEGER DEFAULT 0,
                countdown_enabled INTEGER DEFAULT 0,
                reminder_enabled INTEGER DEFAULT 0,
                email_consent INTEGER DEFAULT 0,
                terms_accepted INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        logger.info("Ensured master users table exists.")
        
        # Add nickname column if it doesn't exist (for migration)
        try:
            conn.execute("ALTER TABLE users ADD COLUMN nickname TEXT")
            logger.info("Added nickname column to users table")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Add consent columns if they don't exist
        try:
            conn.execute("ALTER TABLE users ADD COLUMN email_consent INTEGER DEFAULT 0")
            logger.info("Added email_consent column to users table")
        except sqlite3.OperationalError:
            pass
        
        try:
            conn.execute("ALTER TABLE users ADD COLUMN terms_accepted INTEGER DEFAULT 0")
            logger.info("Added terms_accepted column to users table")
        except sqlite3.OperationalError:
            pass
        
        # Weather subscriptions module table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS weather_subscriptions (
                email TEXT PRIMARY KEY,
                location TEXT NOT NULL,
                personality TEXT DEFAULT 'neutral',
                language TEXT DEFAULT 'en',
                last_sent_date TEXT,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE
            )
        """)
        logger.info("Ensured weather_subscriptions table exists.")
        
        # Countdowns module table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS countdowns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                name TEXT NOT NULL,
                date TEXT NOT NULL,
                yearly INTEGER DEFAULT 0,
                message_before TEXT,
                message_after TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE
            )
        """)
        logger.info("Ensured countdowns table exists.")
        
        # Add created_at column to countdowns if it doesn't exist (migration)
        try:
            conn.execute("ALTER TABLE countdowns ADD COLUMN created_at TEXT")
            logger.info("Added created_at column to countdowns table")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Reminders table for calendar service
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                message TEXT NOT NULL,
                first_run_at TEXT NOT NULL,
                remaining_repeats INTEGER NOT NULL,
                last_sent_at TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE
            )
        """)
        logger.info("Ensured reminders table exists.")
        
        # Inbox log for deduplication
        conn.execute("""
            CREATE TABLE IF NOT EXISTS inbox_log (
                uid TEXT PRIMARY KEY,
                from_email TEXT NOT NULL,
                received_at TEXT NOT NULL,
                subject TEXT,
                body_hash TEXT
            )
        """)
        logger.info("Ensured inbox_log table exists.")
        
        # Password reset tokens table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                token TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                expires_at TEXT NOT NULL,
                used INTEGER DEFAULT 0,
                used_at TEXT
            )
        """)
        logger.info("Ensured password_reset_tokens table exists.")
        
        # Create indexes for performance
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_weather 
            ON users(weather_enabled) WHERE weather_enabled = 1
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_countdown 
            ON users(countdown_enabled) WHERE countdown_enabled = 1
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_reminder 
            ON users(reminder_enabled) WHERE reminder_enabled = 1
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_countdowns_email 
            ON countdowns(email)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_reminders_email_time 
            ON reminders(email, first_run_at)
        """)
        logger.info("Ensured all indexes exist.")
        
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Database initialization error: {e}")
        raise
    finally:
        conn.close()


def main():
    logger.info("Starting Daily Brief Service...")
    config = load_env()
    db_path = os.getenv("APP_DB_PATH", "app.db")
    init_db(db_path)

    global scheduler
    scheduler = BlockingScheduler()

    # Schedule daily weather job to run at 5 AM daily (change to */5 for testing)
    scheduler.add_job(
        lambda: run_daily_job(config),
        #CronTrigger(hour=5, minute=0, timezone=config.timezone),
        CronTrigger(minute='*/5', timezone=config.timezone),  # For testing: every 5 minutes
        replace_existing=True
    )
    
    logger.info(f"📅 Scheduler configured: Daily emails at 5:00 AM {config.timezone}")

    # Start email monitor in a separate thread
    start_email_monitor()

    logger.info("✅ Daily Brief Service is running. Press Ctrl+C to stop.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main()