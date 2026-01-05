#!/usr/bin/env python3
"""
Migration: Remove lat and lon columns from users table
These should only exist in weather_subscriptions table
"""
import os
import sys
import sqlite3

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

def migrate():
    """Remove lat and lon columns from users table."""
    db_path = os.getenv("APP_DB_PATH", "app.db")
    
    print("=" * 60)
    print("Migration: Remove lat/lon from users table")
    print(f"Database: {db_path}")
    print("=" * 60)
    print()
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    try:
        # Check if columns exist
        cursor = conn.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        
        has_lat = 'lat' in columns
        has_lon = 'lon' in columns
        
        print(f"Current users table columns: {', '.join(columns)}")
        print(f"Has lat column: {has_lat}")
        print(f"Has lon column: {has_lon}")
        print()
        
        if not has_lat and not has_lon:
            print("✅ Migration not needed - lat/lon columns don't exist")
            return True
        
        print("🔧 Creating new users table without lat/lon...")
        
        # SQLite doesn't support DROP COLUMN directly, so we need to recreate the table
        # 1. Rename old table
        conn.execute("ALTER TABLE users RENAME TO users_old")
        
        # 2. Create new table without lat/lon
        conn.execute("""
            CREATE TABLE users (
                email TEXT PRIMARY KEY,
                username TEXT,
                nickname TEXT,
                password_hash TEXT,
                timezone TEXT DEFAULT 'UTC',
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
        
        # 3. Copy data from old table (excluding lat/lon)
        conn.execute("""
            INSERT INTO users (
                email, username, nickname, password_hash, timezone,
                subscription_type, weather_enabled, countdown_enabled, reminder_enabled,
                email_consent, terms_accepted, created_at, updated_at
            )
            SELECT 
                email, username, nickname, password_hash, timezone,
                subscription_type, weather_enabled, countdown_enabled, reminder_enabled,
                email_consent, terms_accepted, created_at, updated_at
            FROM users_old
        """)
        
        # 4. Drop old table
        conn.execute("DROP TABLE users_old")
        
        conn.commit()
        
        print("✅ Migration completed successfully!")
        print()
        
        # Verify
        cursor = conn.execute("PRAGMA table_info(users)")
        new_columns = [row[1] for row in cursor.fetchall()]
        print(f"New users table columns: {', '.join(new_columns)}")
        
        # Count records
        count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        print(f"Total users: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = migrate()
    sys.exit(0 if success else 1)
