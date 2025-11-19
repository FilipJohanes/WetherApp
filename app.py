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
import sys
import logging
import signal
import argparse
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from services.weather_service import run_daily_weather_job, list_subscribers
from services.email_service import start_email_monitor, stop_email_monitor, send_test_email
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
class SafeStreamHandler(logging.StreamHandler):
    """Custom stream handler that safely handles Unicode characters"""
    def emit(self, record):
        try:
            super().emit(record)
        except UnicodeEncodeError:
            # Fallback: encode with ascii and replace problem characters
            msg = self.format(record)
            safe_msg = msg.encode('ascii', errors='replace').decode('ascii')
            record.msg = safe_msg
            super().emit(record)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        SafeStreamHandler(sys.stderr),
        logging.FileHandler('app.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

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
    
    os._exit(0)

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
    
    # Set timezone globally
    os.environ['TZ'] = config.timezone
    
    logger.info(f"Configuration loaded - Email: {config.email_address}, TZ: {config.timezone}")
    return config


def init_db(path: str = "app.db") -> None:
    """Initialize SQLite database with required tables."""
    logger.info(f"Initializing database at {path}")
    
    conn = sqlite3.connect(path)
    try:
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
        
        conn.commit()
        logger.info("Database initialized successfully")
        
    finally:
        conn.close()


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(description="Daily Brief Service")
    parser.add_argument("--dry-run", action="store_true", help="Run without sending emails")
    parser.add_argument("--list-subs", action="store_true", help="List weather subscribers")
    parser.add_argument("--list-reminders", action="store_true", help="List pending reminders")
    parser.add_argument("--send-test", metavar="EMAIL", help="Send test email to address")
    
    args = parser.parse_args()
    
    # Create README on first run
    create_readme_if_missing()
    
    # Initialize database
    init_db()
    
    if args.list_subs:
        list_subscribers()
        return
        
    if args.list_reminders:
        list_reminders()
        return
    
    if args.send_test:
        config = load_env()
        send_test_email(config, args.send_test)
        return
    
    logger.info("Starting Daily Brief Service")
    config = load_env()
    
    if args.dry_run:
        logger.info("Running in DRY RUN mode - no emails will be sent")
    
    global scheduler
    scheduler = BlockingScheduler(timezone=config.timezone)
    
    start_email_monitor(config, args.dry_run)
    
    # Schedule jobs - only weather checking, emails are handled real-time
    # Reminder system temporarily disabled
    # scheduler.add_job(lambda: run_due_reminders_job(config, args.dry_run), CronTrigger(minute=1), id='check_reminders', name='Send due calendar reminders')
    scheduler.add_job(
        func=lambda: run_daily_weather_job(config, args.dry_run),
        trigger=CronTrigger(minute=0),
        id='daily_weather',
        name='Check hourly for 5 AM deliveries'
    )
    
    logger.info("Scheduler started - Daily Brief Service is running")
    logger.info("Jobs scheduled:")
    logger.info("  - Email monitoring: real-time IMAP IDLE (immediate response)")
    # logger.info("  - Check reminders: every 1 minute")  # Disabled
    logger.info("  - Daily weather: check at :00 of every hour, send at 5 AM local time per subscriber")
    logger.info("🎯 Press Ctrl+C to stop the service gracefully")
    
    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("🛑 Keyboard interrupt received")
        signal_handler(signal.SIGINT, None)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        if scheduler and scheduler.running:
            scheduler.shutdown()
        raise


if __name__ == "__main__":
    main()