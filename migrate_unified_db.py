"""
Database Migration Script - Unified Schema
Migrates from old fragmented database to new unified structure with master users table.
"""
import sqlite3
import os
from datetime import datetime
import shutil

DB_PATH = "app.db"
BACKUP_PATH = f"app_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

def backup_database():
    """Create a backup of the existing database."""
    if os.path.exists(DB_PATH):
        shutil.copy2(DB_PATH, BACKUP_PATH)
        print(f"✅ Backup created: {BACKUP_PATH}")
    else:
        print("⚠️  No existing database found, starting fresh")

def create_new_schema(conn):
    """Create the new unified database schema."""
    
    # Master users table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users_new (
            email TEXT PRIMARY KEY,
            username TEXT,
            password_hash TEXT,
            timezone TEXT DEFAULT 'UTC',
            lat REAL,
            lon REAL,
            subscription_type TEXT DEFAULT 'free',
            weather_enabled INTEGER DEFAULT 0,
            countdown_enabled INTEGER DEFAULT 0,
            reminder_enabled INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    print("✅ Created users_new table")
    
    # Weather subscriptions module table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS weather_subscriptions (
            email TEXT PRIMARY KEY,
            location TEXT NOT NULL,
            personality TEXT DEFAULT 'neutral',
            language TEXT DEFAULT 'en',
            last_sent_date TEXT,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (email) REFERENCES users_new(email) ON DELETE CASCADE
        )
    """)
    print("✅ Created weather_subscriptions table")
    
    # Countdowns module table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS countdowns_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            yearly INTEGER DEFAULT 0,
            message_before TEXT,
            message_after TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (email) REFERENCES users_new(email) ON DELETE CASCADE
        )
    """)
    print("✅ Created countdowns_new table")
    
    # Reminders table (keep structure, just ensure FK)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reminders_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            first_run_at TEXT NOT NULL,
            remaining_repeats INTEGER NOT NULL,
            last_sent_at TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (email) REFERENCES users_new(email) ON DELETE CASCADE
        )
    """)
    print("✅ Created reminders_new table")
    
    # Inbox log (unchanged)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS inbox_log_new (
            uid TEXT PRIMARY KEY,
            from_email TEXT NOT NULL,
            received_at TEXT NOT NULL,
            subject TEXT,
            body_hash TEXT
        )
    """)
    print("✅ Created inbox_log_new table")
    
    conn.commit()

def migrate_data(conn):
    """Migrate data from old tables to new unified structure."""
    now = datetime.utcnow().isoformat()
    
    # Check if old tables exist
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    table_names = [t[0] for t in tables]
    
    # Collect all unique users from various sources
    all_users = {}
    
    # From old subscribers table
    if 'subscribers' in table_names:
        print("📊 Migrating from subscribers table...")
        rows = conn.execute("""
            SELECT email, location, lat, lon, timezone, personality, language, 
                   updated_at, last_sent_date, countdown_enabled, reminder_enabled
            FROM subscribers
        """).fetchall()
        
        for row in rows:
            email = row[0]
            all_users[email] = {
                'email': email,
                'username': None,
                'password_hash': None,
                'timezone': row[4] or 'UTC',
                'lat': row[2],
                'lon': row[3],
                'subscription_type': 'free',
                'weather_enabled': 1,  # They're in subscribers, so weather is enabled
                'countdown_enabled': row[9] if len(row) > 9 else 0,
                'reminder_enabled': row[10] if len(row) > 10 else 0,
                'created_at': row[7] or now,
                'updated_at': row[7] or now,
                'weather_data': {
                    'location': row[1],
                    'personality': row[5] or 'neutral',
                    'language': row[6] or 'en',
                    'last_sent_date': row[8] if len(row) > 8 else None,
                    'updated_at': row[7] or now
                }
            }
        print(f"  ✅ Found {len(rows)} subscribers")
    
    # From old weather table (if it exists separately)
    if 'weather' in table_names:
        print("📊 Migrating from weather table...")
        rows = conn.execute("""
            SELECT email, location, lat, lon, timezone, personality, language, updated_at
            FROM weather
        """).fetchall()
        
        for row in rows:
            email = row[0]
            if email not in all_users:
                all_users[email] = {
                    'email': email,
                    'username': None,
                    'password_hash': None,
                    'timezone': row[4] or 'UTC',
                    'lat': row[2],
                    'lon': row[3],
                    'subscription_type': 'free',
                    'weather_enabled': 1,
                    'countdown_enabled': 0,
                    'reminder_enabled': 0,
                    'created_at': row[7] or now,
                    'updated_at': row[7] or now,
                }
            all_users[email]['weather_data'] = {
                'location': row[1],
                'personality': row[5] or 'neutral',
                'language': row[6] or 'en',
                'last_sent_date': None,
                'updated_at': row[7] or now
            }
        print(f"  ✅ Found {len(rows)} weather entries")
    
    # From old users table (for password/auth data)
    if 'users' in table_names:
        print("📊 Merging from old users table...")
        rows = conn.execute("""
            SELECT email, password_hash, timezone, personality, language, 
                   created_at, weather_enabled, countdown_enabled, reminder_enabled
            FROM users
        """).fetchall()
        
        for row in rows:
            email = row[0]
            if email in all_users:
                # Merge auth data into existing user
                all_users[email]['password_hash'] = row[1]
                if row[5]:  # Use older created_at if available
                    all_users[email]['created_at'] = row[5]
                # Update module flags from old users table
                if len(row) > 6:
                    all_users[email]['weather_enabled'] = row[6]
                if len(row) > 7:
                    all_users[email]['countdown_enabled'] = row[7]
                if len(row) > 8:
                    all_users[email]['reminder_enabled'] = row[8]
            else:
                # New user only in old users table
                all_users[email] = {
                    'email': email,
                    'username': None,
                    'password_hash': row[1],
                    'timezone': row[2] or 'UTC',
                    'lat': None,
                    'lon': None,
                    'subscription_type': 'free',
                    'weather_enabled': row[6] if len(row) > 6 else 0,
                    'countdown_enabled': row[7] if len(row) > 7 else 0,
                    'reminder_enabled': row[8] if len(row) > 8 else 0,
                    'created_at': row[5] or now,
                    'updated_at': now
                }
        print(f"  ✅ Merged {len(rows)} user records")
    
    # Insert all users into new master table
    print(f"📝 Inserting {len(all_users)} users into master table...")
    for email, user in all_users.items():
        conn.execute("""
            INSERT INTO users_new (
                email, username, password_hash, timezone, lat, lon,
                subscription_type, weather_enabled, countdown_enabled, reminder_enabled,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user['email'], user['username'], user['password_hash'],
            user['timezone'], user['lat'], user['lon'],
            user['subscription_type'], user['weather_enabled'],
            user['countdown_enabled'], user['reminder_enabled'],
            user['created_at'], user['updated_at']
        ))
        
        # Insert weather subscription data if exists
        if 'weather_data' in user and user['weather_enabled']:
            wd = user['weather_data']
            conn.execute("""
                INSERT INTO weather_subscriptions (
                    email, location, personality, language, last_sent_date, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                email, wd['location'], wd['personality'],
                wd['language'], wd.get('last_sent_date'), wd['updated_at']
            ))
    
    conn.commit()
    print(f"  ✅ Inserted {len(all_users)} users")
    
    # Migrate countdowns
    if 'countdowns' in table_names:
        print("📊 Migrating countdowns...")
        rows = conn.execute("""
            SELECT email, name, date, yearly, message_before, message_after
            FROM countdowns
        """).fetchall()
        
        migrated_countdowns = 0
        for row in rows:
            email = row[0]
            # Only migrate if user exists in new master table
            if email in all_users:
                conn.execute("""
                    INSERT INTO countdowns_new (
                        email, name, date, yearly, message_before, message_after, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (email, row[1], row[2], row[3], row[4], row[5], now))
                migrated_countdowns += 1
                
                # Enable countdown in master table if not already
                conn.execute("""
                    UPDATE users_new SET countdown_enabled = 1 WHERE email = ?
                """, (email,))
        
        conn.commit()
        print(f"  ✅ Migrated {migrated_countdowns} countdowns")
    
    # Migrate reminders
    if 'reminders' in table_names:
        print("📊 Migrating reminders...")
        rows = conn.execute("""
            SELECT email, message, first_run_at, remaining_repeats, last_sent_at, created_at
            FROM reminders
        """).fetchall()
        
        for row in rows:
            conn.execute("""
                INSERT INTO reminders_new (
                    email, message, first_run_at, remaining_repeats, last_sent_at, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, row)
        
        conn.commit()
        print(f"  ✅ Migrated {len(rows)} reminders")
    
    # Migrate inbox_log
    if 'inbox_log' in table_names:
        print("📊 Migrating inbox_log...")
        rows = conn.execute("""
            SELECT uid, from_email, received_at, subject, body_hash
            FROM inbox_log
        """).fetchall()
        
        for row in rows:
            conn.execute("""
                INSERT INTO inbox_log_new (
                    uid, from_email, received_at, subject, body_hash
                ) VALUES (?, ?, ?, ?, ?)
            """, row)
        
        conn.commit()
        print(f"  ✅ Migrated {len(rows)} inbox log entries")

def swap_tables(conn):
    """Drop old tables and rename new ones."""
    print("🔄 Swapping tables...")
    
    # Drop old tables
    old_tables = ['users', 'subscribers', 'weather', 'countdowns', 'reminders', 'inbox_log']
    for table in old_tables:
        try:
            conn.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"  ✅ Dropped old table: {table}")
        except sqlite3.Error as e:
            print(f"  ⚠️  Could not drop {table}: {e}")
    
    # Rename new tables
    rename_map = {
        'users_new': 'users',
        'countdowns_new': 'countdowns',
        'reminders_new': 'reminders',
        'inbox_log_new': 'inbox_log'
    }
    
    for old_name, new_name in rename_map.items():
        conn.execute(f"ALTER TABLE {old_name} RENAME TO {new_name}")
        print(f"  ✅ Renamed {old_name} → {new_name}")
    
    conn.commit()
    print("✅ Table swap complete")

def create_indexes(conn):
    """Create indexes for performance."""
    print("📇 Creating indexes...")
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_users_weather ON users(weather_enabled) WHERE weather_enabled = 1",
        "CREATE INDEX IF NOT EXISTS idx_users_countdown ON users(countdown_enabled) WHERE countdown_enabled = 1",
        "CREATE INDEX IF NOT EXISTS idx_users_reminder ON users(reminder_enabled) WHERE reminder_enabled = 1",
        "CREATE INDEX IF NOT EXISTS idx_countdowns_email ON countdowns(email)",
        "CREATE INDEX IF NOT EXISTS idx_reminders_email ON reminders(email)",
    ]
    
    for idx_sql in indexes:
        conn.execute(idx_sql)
    
    conn.commit()
    print("✅ Indexes created")

def verify_migration(conn):
    """Verify the migration was successful."""
    print("\n🔍 Verifying migration...")
    
    tables = {
        'users': 'SELECT COUNT(*) FROM users',
        'weather_subscriptions': 'SELECT COUNT(*) FROM weather_subscriptions',
        'countdowns': 'SELECT COUNT(*) FROM countdowns',
        'reminders': 'SELECT COUNT(*) FROM reminders',
        'inbox_log': 'SELECT COUNT(*) FROM inbox_log'
    }
    
    for table, query in tables.items():
        try:
            count = conn.execute(query).fetchone()[0]
            print(f"  ✅ {table}: {count} rows")
        except sqlite3.Error as e:
            print(f"  ❌ {table}: Error - {e}")
    
    # Check foreign key integrity
    print("\n🔗 Checking foreign key integrity...")
    conn.execute("PRAGMA foreign_keys = ON")
    integrity_check = conn.execute("PRAGMA foreign_key_check").fetchall()
    if not integrity_check:
        print("  ✅ All foreign keys are valid")
    else:
        print(f"  ⚠️  Foreign key issues found: {integrity_check}")

def main():
    """Main migration process."""
    print("=" * 60)
    print("DATABASE MIGRATION - UNIFIED SCHEMA")
    print("=" * 60)
    
    # Backup
    backup_database()
    
    # Connect and migrate
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = OFF")  # Disable during migration
    
    try:
        create_new_schema(conn)
        migrate_data(conn)
        swap_tables(conn)
        create_indexes(conn)
        
        conn.execute("PRAGMA foreign_keys = ON")  # Re-enable
        verify_migration(conn)
        
        print("\n" + "=" * 60)
        print("✅ MIGRATION COMPLETE!")
        print("=" * 60)
        print(f"Backup saved as: {BACKUP_PATH}")
        print("New unified database structure is ready.")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print(f"Your original database is backed up at: {BACKUP_PATH}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()
