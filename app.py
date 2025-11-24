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
from services.countdown_service import init_countdown_db

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


def init_db(path: str = "app.db") -> None:
    """Initialize SQLite database with required tables."""
    logger.info(f"Initializing database at {path}")
    conn = sqlite3.connect(path)
    try:
        # Rename subscribers table to weather if it exists
        try:
            conn.execute("ALTER TABLE subscribers RENAME TO weather")
            logger.info("Renamed subscribers table to weather.")
        except sqlite3.OperationalError:
            # Table may not exist or already renamed
            pass
        # Master users table for quick access and subscriptions
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                active INTEGER DEFAULT 1,
                weather_enabled INTEGER DEFAULT 0,
                countdown_enabled INTEGER DEFAULT 0,
                reminder_enabled INTEGER DEFAULT 0,
                timezone TEXT DEFAULT 'UTC',
                last_active TEXT,
                created_at TEXT,
                personality TEXT DEFAULT 'neutral',
                language TEXT DEFAULT 'en'
            )
        """)
        logger.info("Ensured master users table exists.")
        # Subscribers table for weather service
        conn.execute("""
            CREATE TABLE IF NOT EXISTS subscribers (
                email TEXT PRIMARY KEY,
                location TEXT NOT NULL,
                lat REAL NULL,
                lon REAL NULL,
                updated_at TEXT NOT NULL,
                personality TEXT DEFAULT 'neutral'
            )
        """)
        
        # Handle schema upgrades - add personality column if it doesn't exist
        try:
            conn.execute("ALTER TABLE subscribers ADD COLUMN personality TEXT DEFAULT 'neutral'")
            logger.info("Added personality column to subscribers table")
        except sqlite3.OperationalError:
            # Column already exists, which is fine
            pass
        
        # Handle schema upgrade - add language column if it doesn't exist
        try:
            conn.execute("ALTER TABLE subscribers ADD COLUMN language TEXT DEFAULT 'en'")
            logger.info("Added language column to subscribers table")
        except sqlite3.OperationalError:
            # Column already exists, which is fine
            pass
        
        # Handle schema upgrade - add timezone column if it doesn't exist
        try:
            conn.execute("ALTER TABLE subscribers ADD COLUMN timezone TEXT DEFAULT 'UTC'")
            logger.info("Added timezone column to subscribers table")
        except sqlite3.OperationalError:
            # Column already exists, which is fine
            pass
        
        # Handle schema upgrade - add last_sent_date column to track daily sends
        try:
            conn.execute("ALTER TABLE subscribers ADD COLUMN last_sent_date TEXT NULL")
            logger.info("Added last_sent_date column to subscribers table")
        except sqlite3.OperationalError:
            # Column already exists, which is fine
            pass

        # Add countdown_enabled column if it doesn't exist
        try:
            conn.execute("ALTER TABLE subscribers ADD COLUMN countdown_enabled INTEGER DEFAULT 0")
            logger.info("Added countdown_enabled column to subscribers table")
        except sqlite3.OperationalError:
            # Column already exists, which is fine
            pass
        # Add reminder_enabled column if it doesn't exist
        try:
            conn.execute("ALTER TABLE subscribers ADD COLUMN reminder_enabled INTEGER DEFAULT 0")
            logger.info("Added reminder_enabled column to subscribers table")
        except sqlite3.OperationalError:
            # Column already exists, which is fine
            pass
        
        # Reminders table for calendar service
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                message TEXT NOT NULL,
                first_run_at TEXT NOT NULL,
                remaining_repeats INTEGER NOT NULL,
                last_sent_at TEXT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        # Index for efficient reminder queries
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_reminders_email_time 
            ON reminders (email, first_run_at)
        """)
        
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
        if scheduler:
            scheduler.start()
    except KeyboardInterrupt:
        logger.info("🛑 Keyboard interrupt received")
        signal_handler(signal.SIGINT, None)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        if scheduler and scheduler.running:
            scheduler.shutdown()
        raise


def main():
    logger.info("Starting Daily Brief Service...")
    config = load_env()
    init_db()
    init_countdown_db()

    global scheduler
    scheduler = BlockingScheduler()

    # Schedule daily weather job to run every hour
    scheduler.add_job(
        lambda: run_daily_job(config),
        CronTrigger(minute=0, timezone=config.timezone),
        #CronTrigger(minute="*/1"),
        replace_existing=True
    )

    # Start email monitor in a separate thread
    start_email_monitor()

    logger.info("✅ Daily Brief Service is running. Press Ctrl+C to stop.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main()