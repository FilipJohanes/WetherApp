"""
Subscription Service Module
Handles all subscriber insert, update, and delete logic for the weather app.
"""
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo

# You may need to import Config from the main app if type checking is required
# from app import Config

def add_or_update_subscriber(email, location, lat, lon, personality, language, timezone, db_path="app.db"):
    """Add a new subscriber or update existing one."""
    conn = sqlite3.connect(db_path)
    try:
        now = datetime.now(ZoneInfo(timezone)).isoformat() if timezone else datetime.now().isoformat()
        conn.execute("""
            INSERT INTO subscribers (email, location, lat, lon, personality, language, timezone, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(email) DO UPDATE SET
                location=excluded.location,
                lat=excluded.lat,
                lon=excluded.lon,
                personality=excluded.personality,
                language=excluded.language,
                timezone=excluded.timezone,
                updated_at=excluded.updated_at
        """, (email, location, lat, lon, personality, language, timezone, now))
        conn.commit()
    finally:
        conn.close()

def delete_subscriber(email, db_path="app.db"):
    """Delete a subscriber by email."""
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.execute("DELETE FROM subscribers WHERE email = ?", (email,))
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()

def get_subscriber(email, db_path="app.db"):
    """Get subscriber info by email."""
    conn = sqlite3.connect(db_path)
    try:
        result = conn.execute("""
            SELECT location, lat, lon, personality, COALESCE(language, 'en'), COALESCE(timezone, 'Europe/Bratislava')
            FROM subscribers WHERE email = ?
        """, (email,)).fetchone()
        return result
    finally:
        conn.close()
