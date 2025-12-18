"""
Verify unified database structure and contents
"""
import sqlite3

DB_PATH = "app.db"

def verify_database():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    print("=" * 70)
    print("UNIFIED DATABASE VERIFICATION")
    print("=" * 70)
    
    # Check master users table
    print("\n📋 MASTER USERS TABLE")
    print("-" * 70)
    users = conn.execute("SELECT * FROM users LIMIT 5").fetchall()
    if users:
        print(f"Columns: {', '.join(users[0].keys())}")
        print(f"Total users: {conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]}")
        print(f"\nSample users:")
        for user in users:
            print(f"  - {user['email']}: weather={user['weather_enabled']}, countdown={user['countdown_enabled']}, reminder={user['reminder_enabled']}")
    
    # Check weather subscriptions
    print("\n🌤️  WEATHER SUBSCRIPTIONS")
    print("-" * 70)
    weather_subs = conn.execute("""
        SELECT ws.*, u.weather_enabled 
        FROM weather_subscriptions ws
        JOIN users u ON ws.email = u.email
        LIMIT 5
    """).fetchall()
    if weather_subs:
        print(f"Total: {conn.execute('SELECT COUNT(*) FROM weather_subscriptions').fetchone()[0]}")
        for ws in weather_subs:
            print(f"  - {ws['email']}: {ws['location']} ({ws['personality']}, {ws['language']}) - Enabled: {bool(ws['weather_enabled'])}")
    
    # Check countdowns
    print("\n⏰ COUNTDOWNS")
    print("-" * 70)
    countdowns = conn.execute("""
        SELECT c.*, u.countdown_enabled 
        FROM countdowns c
        JOIN users u ON c.email = u.email
    """).fetchall()
    if countdowns:
        print(f"Total: {len(countdowns)}")
        for cd in countdowns:
            print(f"  - {cd['email']}: {cd['name']} on {cd['date']} (yearly={cd['yearly']}) - Enabled: {bool(cd['countdown_enabled'])}")
    else:
        print("  No countdowns found")
    
    # Check indexes
    print("\n📇 INDEXES")
    print("-" * 70)
    indexes = conn.execute("""
        SELECT name, tbl_name FROM sqlite_master 
        WHERE type='index' AND name NOT LIKE 'sqlite_%'
    """).fetchall()
    for idx in indexes:
        print(f"  - {idx['name']} on {idx['tbl_name']}")
    
    # Check foreign keys
    print("\n🔗 FOREIGN KEY INTEGRITY")
    print("-" * 70)
    conn.execute("PRAGMA foreign_keys = ON")
    fk_check = conn.execute("PRAGMA foreign_key_check").fetchall()
    if not fk_check:
        print("  ✅ All foreign keys are valid")
    else:
        print(f"  ⚠️  Foreign key issues: {fk_check}")
    
    # Module usage stats
    print("\n📊 MODULE USAGE STATISTICS")
    print("-" * 70)
    stats = conn.execute("""
        SELECT 
            COUNT(*) as total_users,
            SUM(weather_enabled) as weather_users,
            SUM(countdown_enabled) as countdown_users,
            SUM(reminder_enabled) as reminder_users
        FROM users
    """).fetchone()
    print(f"  Total users: {stats['total_users']}")
    print(f"  Weather enabled: {stats['weather_users']}")
    print(f"  Countdown enabled: {stats['countdown_users']}")
    print(f"  Reminder enabled: {stats['reminder_users']}")
    
    conn.close()
    
    print("\n" + "=" * 70)
    print("✅ VERIFICATION COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    verify_database()
