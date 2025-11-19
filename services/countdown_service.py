
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

# DB helpers
COUNTDOWN_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS countdowns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    name TEXT NOT NULL,
    date TEXT NOT NULL,
    yearly INTEGER NOT NULL,
    message_before TEXT,
    message_after TEXT
);
"""

def init_countdown_db(path: str = "app.db"):
    conn = sqlite3.connect(path)
    try:
        conn.execute(COUNTDOWN_TABLE_SQL)
        conn.commit()
    finally:
        conn.close()

def add_countdown(event: CountdownEvent, path: str = "app.db"):
    conn = sqlite3.connect(path)
    try:
        conn.execute("""
            INSERT INTO countdowns (email, name, date, yearly, message_before, message_after)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (event.email, event.name, event.date, int(event.yearly), event.message_before, event.message_after))
        conn.commit()
    finally:
        conn.close()

def get_user_countdowns(email: str, path: str = "app.db") -> List[CountdownEvent]:
    conn = sqlite3.connect(path)
    try:
        rows = conn.execute("SELECT name, date, yearly, message_before, message_after FROM countdowns WHERE email = ?", (email,)).fetchall()
        events = [CountdownEvent(name, date, bool(yearly), email, message_before, message_after) for name, date, yearly, message_before, message_after in rows]
        return events
    finally:
        conn.close()

def delete_countdown(email: str, name: str, path: str = "app.db"):
    conn = sqlite3.connect(path)
    try:
        conn.execute("DELETE FROM countdowns WHERE email = ? AND name = ?", (email, name))
        conn.commit()
    finally:
        conn.close()

def generate_countdown_summary(email: str, today: datetime, tz: str = "Europe/Bratislava", path: str = "app.db") -> str:
    events = get_user_countdowns(email, path)
    if not events:
        return ""
    summary = ""
    now = today.astimezone(ZoneInfo(tz))
    for event in events:
        msg = event.get_countdown_message(now)
        if msg:
            summary += f"{event.name}: {msg}\n"
    return summary.strip()
