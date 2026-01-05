"""
Subscription Service Module
Handles weather subscription insert, update, and delete logic with unified schema.
"""
import os
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo

def add_or_update_subscriber(email, location, lat, lon, personality, language, timezone, db_path=None):
    """Add or update a weather subscription. Creates user if doesn't exist."""
    if db_path is None:
        db_path = os.getenv("APP_DB_PATH", "app.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        now = datetime.now(ZoneInfo(timezone)).isoformat() if timezone else datetime.utcnow().isoformat()
        
        # Ensure user exists in master table
        user_exists = conn.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone()
        if not user_exists:
            # Create new user
            print(f"[SUBSCRIPTION] Creating new user: {email}")
            cursor = conn.execute("""
                INSERT INTO users (email, timezone, weather_enabled, created_at, updated_at)
                VALUES (?, ?, 1, ?, ?)
            """, (email, timezone, now, now))
            print(f"[SUBSCRIPTION] User created, rowcount: {cursor.rowcount}")
        else:
            # Update existing user
            print(f"[SUBSCRIPTION] Updating existing user: {email}, setting weather_enabled=1")
            cursor = conn.execute("""
                UPDATE users SET timezone = ?, weather_enabled = 1, updated_at = ?
                WHERE email = ?
            """, (timezone, now, email))
            print(f"[SUBSCRIPTION] User updated, rowcount: {cursor.rowcount}")
            if cursor.rowcount == 0:
                print(f"[SUBSCRIPTION] WARNING: UPDATE affected 0 rows for {email}")
        
        # Insert or update weather subscription
        print(f"[SUBSCRIPTION] Creating/updating weather subscription for {email}")
        cursor = conn.execute("""
            INSERT INTO weather_subscriptions (email, location, lat, lon, personality, language, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(email) DO UPDATE SET
                location=excluded.location,
                lat=excluded.lat,
                lon=excluded.lon,
                personality=excluded.personality,
                language=excluded.language,
                updated_at=excluded.updated_at
        """, (email, location, lat, lon, personality, language, now))
        print(f"[SUBSCRIPTION] Weather subscription saved, rowcount: {cursor.rowcount}")
        
        conn.commit()
        print(f"[SUBSCRIPTION] Transaction committed successfully for {email}")
        
        # Verify the data was saved correctly
        verify = conn.execute("""
            SELECT u.email, u.weather_enabled, ws.location
            FROM users u
            LEFT JOIN weather_subscriptions ws ON u.email = ws.email
            WHERE u.email = ?
        """, (email,)).fetchone()
        if verify:
            print(f"[SUBSCRIPTION] Verification: email={verify['email']}, weather_enabled={verify['weather_enabled']}, location={verify['location']}")
        else:
            print(f"[SUBSCRIPTION] ERROR: Could not verify data for {email}")
            
    except Exception as e:
        print(f"[SUBSCRIPTION] ERROR: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        conn.close()

def delete_subscriber(email, db_path=None):
    """Delete a weather subscription and disable weather module for user."""
    if db_path is None:
        db_path = os.getenv("APP_DB_PATH", "app.db")
    conn = sqlite3.connect(db_path)
    try:
        # Delete weather subscription
        cursor = conn.execute("DELETE FROM weather_subscriptions WHERE email = ?", (email,))
        deleted = cursor.rowcount
        
        # Disable weather module in user table
        if deleted > 0:
            now = datetime.utcnow().isoformat()
            conn.execute("""
                UPDATE users SET weather_enabled = 0, updated_at = ? WHERE email = ?
            """, (now, email))
        
        conn.commit()
        return deleted
    finally:
        conn.close()

def get_subscriber(email, db_path=None):
    """Get weather subscription info by email."""
    if db_path is None:
        db_path = os.getenv("APP_DB_PATH", "app.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        result = conn.execute("""
            SELECT ws.location, ws.lat, ws.lon, ws.personality, 
                   COALESCE(ws.language, 'en') as language,
                   COALESCE(u.timezone, 'UTC') as timezone
            FROM weather_subscriptions ws
            JOIN users u ON ws.email = u.email
            WHERE ws.email = ?
        """, (email,)).fetchone()
        return result
    finally:
        conn.close()
