import os
import sqlite3
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import List, Optional

class CountdownEvent:
    def __init__(self, name: str, date: str, yearly: bool, email: str, message_before: Optional[str] = None, message_after: Optional[str] = None):
        self.name = name
        self.date = date  # ISO format: YYYY-MM-DD
        self.yearly = yearly
        self.email = email
        self.message_before = message_before or f"Days to {name}: {{days}}"
        self.message_after = message_after  # If None, disables after event

    def get_next_event_date(self, today: datetime) -> Optional[datetime]:
        event_date = datetime.strptime(self.date, "%Y-%m-%d")
        # Make event_date timezone-aware if today is aware
        if today.tzinfo is not None and event_date.tzinfo is None:
            event_date = event_date.replace(tzinfo=today.tzinfo)
        if self.yearly:
            event_date = event_date.replace(year=today.year)
            if event_date < today:
                event_date = event_date.replace(year=today.year + 1)
        return event_date

    def get_countdown_message(self, today: datetime) -> Optional[str]:
        event_date = self.get_next_event_date(today)
        if event_date > today:
            days = (event_date - today).days
            return self.message_before.replace("{days}", str(days))
        elif self.message_after:
            days_since = (today - event_date).days
            return self.message_after.replace("{days}", str(days_since))
        else:
            return None  # Countdown disables after event if no message_after

# DB helpers - No longer need init_countdown_db, handled in main init_db()

def add_countdown(event: CountdownEvent, path: str = None):
    """Add a countdown for a user. Ensures user exists and enables countdown module."""
    if path is None:
        path = os.getenv("APP_DB_PATH", "app.db")
    
    # Validate event data
    if not event.name or not event.name.strip():
        raise ValueError("Countdown name cannot be empty.")
    if not event.date or not event.date.strip():
        raise ValueError("Countdown date cannot be empty.")
    if not event.email or not event.email.strip():
        raise ValueError("Email cannot be empty.")
    
    # Validate date format
    try:
        datetime.strptime(event.date, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid date format: {event.date}. Expected YYYY-MM-DD.")
    
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        # Check for duplicate
        existing = conn.execute(
            "SELECT 1 FROM countdowns WHERE email = ? AND name = ? AND date = ?",
            (event.email, event.name, event.date)
        ).fetchone()
        if existing:
            raise ValueError(f"Countdown for '{event.name}' on {event.date} already exists.")
        
        # Ensure user exists in users table first
        user_exists = conn.execute(
            "SELECT 1 FROM users WHERE email = ?",
            (event.email,)
        ).fetchone()
        
        now = datetime.utcnow().isoformat()
        
        if not user_exists:
            # Create user record if it doesn't exist
            conn.execute("""
                INSERT INTO users (email, username, timezone, weather_enabled, countdown_enabled, reminder_enabled, created_at, updated_at)
                VALUES (?, ?, 'UTC', 0, 1, 0, ?, ?)
            """, (event.email, event.email.split('@')[0], now, now))
        else:
            # Enable countdown module for existing user
            conn.execute("""
                UPDATE users SET countdown_enabled = 1, updated_at = ? WHERE email = ?
            """, (now, event.email))
        
        # Insert countdown with created_at timestamp (handle NULL for existing rows without created_at)
        conn.execute("""
            INSERT INTO countdowns (email, name, date, yearly, message_before, message_after, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (event.email, event.name, event.date, int(event.yearly), event.message_before, event.message_after, now))
        
        conn.commit()
    finally:
        conn.close()

def get_user_countdowns(email: str, path: str = None) -> List[CountdownEvent]:
    if path is None:
        path = os.getenv("APP_DB_PATH", "app.db")
    conn = sqlite3.connect(path)
    try:
        rows = conn.execute("SELECT name, date, yearly, message_before, message_after FROM countdowns WHERE email = ?", (email,)).fetchall()
        events = [CountdownEvent(name, date, bool(yearly), email, message_before, message_after) for name, date, yearly, message_before, message_after in rows]
        return events
    finally:
        conn.close()

def delete_countdown(email: str, name: str, path: str = "app.db"):
    """Delete a countdown and disable module if user has no more countdowns."""
    conn = sqlite3.connect(path)
    try:
        conn.execute("DELETE FROM countdowns WHERE email = ? AND name = ?", (email, name))
        
        # Check if user has any remaining countdowns
        remaining = conn.execute(
            "SELECT COUNT(*) as count FROM countdowns WHERE email = ?", (email,)
        ).fetchone()[0]
        
        # If no countdowns left, disable the module
        if remaining == 0:
            now = datetime.utcnow().isoformat()
            conn.execute("""
                UPDATE users SET countdown_enabled = 0, updated_at = ? WHERE email = ?
            """, (now, email))
        
        conn.commit()
    finally:
        conn.close()

def generate_countdown_summary(email: str, today: datetime, tz: str = "Europe/Bratislava", path: str = "app.db") -> str:
    events = get_user_countdowns(email, path)
    if not events:
        return ""
    summary = ""
    # Ensure 'today' is timezone-aware
    if today.tzinfo is None:
        now = today.replace(tzinfo=ZoneInfo(tz))
    else:
        now = today.astimezone(ZoneInfo(tz))
    def get_days_word(days, language):
        if language == "sk":
            if days == 1:
                return "deň"
            elif 2 <= days <= 4:
                return "dni"
            else:
                return "dní"
        elif language == "es":
            return "día" if days == 1 else "días"
        else:
            return "day" if days == 1 else "days"

    for event in events:
        event_date = event.get_next_event_date(now)
        if event_date:
            if event_date > now:
                days_number = (event_date - now).days
            else:
                days_number = (now - event_date).days
        else:
            days_number = "?"
        msg = event.get_countdown_message(now)
        # Try to get language from event, fallback to 'en'
        language = getattr(event, 'language', 'en')
        days_word = get_days_word(days_number if isinstance(days_number, int) else 2, language)
        if msg:
            # If {days_number} is not already replaced in msg, append days
            if "{days_number}" not in event.message_before and "{days_number}" not in event.message_after:
                summary += f"{msg}: {days_number} {days_word}\n"
            else:
                summary += f"{msg}\n"
    return summary.strip()
