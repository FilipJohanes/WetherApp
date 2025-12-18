#!/usr/bin/env python3
"""
Manual test script: Show database statistics.
Displays subscriber counts, languages, personalities, and recent activity.
"""
import os
import sys
import sqlite3
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def show_stats(db_path='app.db'):
    """Display comprehensive database statistics."""
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║              Daily Brief Service Statistics                 ║
║              Database: {db_path:<40} ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # Total subscribers
    total = conn.execute("SELECT COUNT(*) as count FROM subscribers").fetchone()['count']
    print(f"📊 TOTAL SUBSCRIBERS: {total}")
    print(f"{'='*60}\n")
    
    if total == 0:
        print("No subscribers found.\n")
        conn.close()
        return
    
    # Language breakdown
    print("🌍 LANGUAGE DISTRIBUTION:")
    print("-" * 60)
    languages = conn.execute("""
        SELECT COALESCE(language, 'unknown') as lang, COUNT(*) as count 
        FROM subscribers 
        GROUP BY language 
        ORDER BY count DESC
    """).fetchall()
    
    for row in languages:
        percentage = (row['count'] / total) * 100
        bar = '█' * int(percentage / 2)
        print(f"  {row['lang']:10} {row['count']:4} ({percentage:5.1f}%) {bar}")
    print()
    
    # Personality breakdown
    print("😊 PERSONALITY DISTRIBUTION:")
    print("-" * 60)
    personalities = conn.execute("""
        SELECT COALESCE(personality, 'unknown') as pers, COUNT(*) as count 
        FROM subscribers 
        GROUP BY personality 
        ORDER BY count DESC
    """).fetchall()
    
    for row in personalities:
        percentage = (row['count'] / total) * 100
        bar = '█' * int(percentage / 2)
        print(f"  {row['pers']:10} {row['count']:4} ({percentage:5.1f}%) {bar}")
    print()
    
    # Timezone breakdown
    print("🌐 TIMEZONE DISTRIBUTION:")
    print("-" * 60)
    timezones = conn.execute("""
        SELECT COALESCE(timezone, 'unknown') as tz, COUNT(*) as count 
        FROM subscribers 
        GROUP BY timezone 
        ORDER BY count DESC
        LIMIT 10
    """).fetchall()
    
    for row in timezones:
        print(f"  {row['tz']:30} {row['count']:4}")
    print()
    
    # Recently updated subscribers
    print("🕒 RECENT ACTIVITY (Last 10 updates):")
    print("-" * 60)
    recent = conn.execute("""
        SELECT email, location, updated_at 
        FROM subscribers 
        ORDER BY updated_at DESC 
        LIMIT 10
    """).fetchall()
    
    for row in recent:
        email_display = row['email'][:30] + '...' if len(row['email']) > 30 else row['email']
        location_display = row['location'][:25] + '...' if len(row['location']) > 25 else row['location']
        updated = row['updated_at'][:19] if row['updated_at'] else 'N/A'
        print(f"  {email_display:33} | {location_display:28} | {updated}")
    print()
    
    # Last sent statistics
    print("📧 EMAIL SENDING STATISTICS:")
    print("-" * 60)
    sent_today = conn.execute("""
        SELECT COUNT(*) as count 
        FROM subscribers 
        WHERE last_sent_date = ?
    """, (datetime.now().date().isoformat(),)).fetchone()['count']
    
    never_sent = conn.execute("""
        SELECT COUNT(*) as count 
        FROM subscribers 
        WHERE last_sent_date IS NULL
    """).fetchone()['count']
    
    print(f"  Sent today:      {sent_today:4}")
    print(f"  Never sent:      {never_sent:4}")
    print()
    
    # Countdown statistics
    print("⏰ COUNTDOWN STATISTICS:")
    print("-" * 60)
    try:
        countdown_total = conn.execute("SELECT COUNT(*) as count FROM countdowns").fetchone()['count']
        print(f"  Total countdowns: {countdown_total}")
        
        if countdown_total > 0:
            upcoming = conn.execute("""
                SELECT name, date, email 
                FROM countdowns 
                WHERE date >= ? 
                ORDER BY date 
                LIMIT 5
            """, (datetime.now().date().isoformat(),)).fetchall()
            
            if upcoming:
                print("\n  Upcoming events:")
                for row in upcoming:
                    print(f"    • {row['date']} - {row['name']} ({row['email']})")
    except sqlite3.OperationalError:
        print("  (Countdown table not found)")
    print()
    
    # Top locations
    print("📍 TOP LOCATIONS:")
    print("-" * 60)
    locations = conn.execute("""
        SELECT location, COUNT(*) as count 
        FROM subscribers 
        GROUP BY location 
        ORDER BY count DESC 
        LIMIT 10
    """).fetchall()
    
    for i, row in enumerate(locations, 1):
        location_display = row['location'][:45] + '...' if len(row['location']) > 45 else row['location']
        print(f"  {i:2}. {location_display:48} ({row['count']})")
    print()
    
    conn.close()
    
    print(f"{'='*60}")
    print("✅ Statistics displayed successfully!")
    print(f"{'='*60}\n")


def main():
    """Main entry point."""
    db_path = os.getenv('APP_DB_PATH', 'app.db')
    
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    
    show_stats(db_path)


if __name__ == '__main__':
    main()
