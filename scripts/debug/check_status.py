#!/usr/bin/env python3
"""Check the current database status and contents."""

import sqlite3
import os

def check_database_status():
    """Check what's in our database."""
    print("=== Database Status Check ===\n")
    
    # Check if database exists
    db_exists = os.path.exists("app.db")
    print(f"📁 Database file exists: {'✅ Yes' if db_exists else '❌ No'}")
    
    if not db_exists:
        print("Database needs to be created first.")
        return
    
    conn = sqlite3.connect("app.db")
    try:
        # Get all tables
        tables = conn.execute("""
            SELECT name FROM sqlite_master WHERE type='table'
        """).fetchall()
        
        print(f"\n📋 Tables found: {len(tables)}")
        for table in tables:
            print(f"  • {table[0]}")
        
        # Check subscribers table
        if any(t[0] == 'subscribers' for t in tables):
            print(f"\n👥 SUBSCRIBERS TABLE:")
            
            # Get table schema
            schema = conn.execute("PRAGMA table_info(subscribers)").fetchall()
            print("  Columns:")
            for col in schema:
                print(f"    • {col[1]} ({col[2]})")
            
            # Count records
            count = conn.execute("SELECT COUNT(*) FROM subscribers").fetchone()[0]
            print(f"  Records: {count}")
            
            if count > 0:
                print("  Sample data:")
                subscribers = conn.execute("""
                    SELECT email, location, personality, 
                           COALESCE(language, 'not set') as language 
                    FROM subscribers LIMIT 5
                """).fetchall()
                for sub in subscribers:
                    print(f"    📧 {sub[0]} -> {sub[1]} ({sub[2]}, {sub[3]})")
        
        # Check reminders table  
        if any(t[0] == 'reminders' for t in tables):
            print(f"\n📅 REMINDERS TABLE:")
            count = conn.execute("SELECT COUNT(*) FROM reminders").fetchone()[0]
            print(f"  Records: {count}")
            
            if count > 0:
                print("  Sample data:")
                reminders = conn.execute("""
                    SELECT email, message, first_run_at, remaining_repeats 
                    FROM reminders LIMIT 3
                """).fetchall()
                for rem in reminders:
                    print(f"    ⏰ {rem[0]}: {rem[1]} (at {rem[2]}, {rem[3]} left)")
        
        # Check inbox_log table
        if any(t[0] == 'inbox_log' for t in tables):
            print(f"\n📨 INBOX_LOG TABLE:")
            count = conn.execute("SELECT COUNT(*) FROM inbox_log").fetchone()[0]
            print(f"  Records: {count}")
    
    finally:
        conn.close()
    
    print(f"\n🌍 LANGUAGE FILES:")
    languages = ['en', 'es', 'sk']
    for lang in languages:
        file_path = f"languages/{lang}/weather_messages.txt"
        exists = os.path.exists(file_path)
        print(f"  {lang.upper()}: {'✅ Ready' if exists else '❌ Missing'}")
    
    print(f"\n✅ System Status: Ready for email processing!")
    print(f"💡 To start the service: python app.py")

if __name__ == "__main__":
    check_database_status()