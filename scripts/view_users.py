#!/usr/bin/env python3
"""
View User Information
Shows all users in the database (passwords are hashed and not shown)
"""

import sqlite3
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

def view_users():
    """Display all users in database."""
    # Get database path
    db_path = os.getenv("APP_DB_PATH", "app.db")
    
    # Resolve path relative to script location
    if not os.path.isabs(db_path):
        script_dir = Path(__file__).parent.parent
        db_path = script_dir / db_path
    
    print(f"📊 Database: {db_path}\n")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    try:
        users = conn.execute("""
            SELECT email, nickname, username, created_at, 
                   weather_enabled, countdown_enabled
            FROM users
            ORDER BY created_at DESC
        """).fetchall()
        
        if not users:
            print("❌ No users found in database")
            return
        
        print(f"👥 Found {len(users)} user(s):\n")
        print("=" * 80)
        
        for user in users:
            print(f"📧 Email:            {user['email']}")
            print(f"   Nickname:         {user['nickname'] or '(not set)'}")
            print(f"   Username:         {user['username'] or '(not set)'}")
            print(f"   Created:          {user['created_at']}")
            print(f"   Weather Enabled:  {bool(user['weather_enabled'])}")
            print(f"   Countdown Enabled: {bool(user['countdown_enabled'])}")
            print(f"   🔒 Password:       [Hashed - use password reset to change]")
            print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    view_users()
