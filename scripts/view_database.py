#!/usr/bin/env python3
"""
Database Inspector - View all data in the Daily Brief Service database
"""

import sqlite3
import os
from datetime import datetime

def inspect_database(db_path="app.db"):
    """Inspect and display all database contents."""
    
    if not os.path.exists(db_path):
        print(f"❌ Database file '{db_path}' not found!")
        return
    
    print("🗄️ Daily Brief Service - Database Inspector")
    print("=" * 50)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"📊 Found {len(tables)} tables: {', '.join([t[0] for t in tables])}\n")
        
        # 1. SUBSCRIBERS TABLE
        print("👤 SUBSCRIBERS TABLE:")
        print("-" * 30)
        try:
            cursor.execute("SELECT * FROM subscribers")
            subscribers = cursor.fetchall()
            
            if subscribers:
                # Get column names
                cursor.execute("PRAGMA table_info(subscribers)")
                columns = [col[1] for col in cursor.fetchall()]
                print(f"Columns: {', '.join(columns)}")
                print()
                
                for i, row in enumerate(subscribers, 1):
                    print(f"🔹 User #{i}:")
                    for col, val in zip(columns, row):
                        if col in ['created_at', 'updated_at'] and val:
                            # Format datetime if it's a timestamp
                            try:
                                dt = datetime.fromisoformat(val.replace('Z', '+00:00'))
                                val = dt.strftime('%Y-%m-%d %H:%M:%S')
                            except:
                                pass
                        print(f"   {col}: {val}")
                    print()
            else:
                print("   📭 No subscribers found")
        except Exception as e:
            print(f"   ❌ Error reading subscribers: {e}")
        
        print()
        
        # 2. REMINDERS TABLE  
        print("⏰ REMINDERS TABLE:")
        print("-" * 30)
        try:
            cursor.execute("SELECT * FROM reminders")
            reminders = cursor.fetchall()
            
            if reminders:
                cursor.execute("PRAGMA table_info(reminders)")
                columns = [col[1] for col in cursor.fetchall()]
                print(f"Columns: {', '.join(columns)}")
                print()
                
                for i, row in enumerate(reminders, 1):
                    print(f"🔹 Reminder #{i}:")
                    for col, val in zip(columns, row):
                        print(f"   {col}: {val}")
                    print()
            else:
                print("   📭 No reminders found")
        except Exception as e:
            print(f"   ❌ Error reading reminders: {e}")
            
        print()
        
        # 3. INBOX LOG TABLE
        print("📧 INBOX LOG (Last 5 emails):")
        print("-" * 30)
        try:
            cursor.execute("SELECT * FROM inbox_log ORDER BY processed_at DESC LIMIT 5")
            logs = cursor.fetchall()
            
            if logs:
                cursor.execute("PRAGMA table_info(inbox_log)")
                columns = [col[1] for col in cursor.fetchall()]
                
                for i, row in enumerate(logs, 1):
                    print(f"🔹 Email #{i}:")
                    for col, val in zip(columns, row):
                        if col == 'processed_at' and val:
                            try:
                                dt = datetime.fromisoformat(val.replace('Z', '+00:00'))
                                val = dt.strftime('%Y-%m-%d %H:%M:%S')
                            except:
                                pass
                        # Truncate long values
                        if isinstance(val, str) and len(val) > 100:
                            val = val[:100] + "..."
                        print(f"   {col}: {val}")
                    print()
            else:
                print("   📭 No email logs found")
        except Exception as e:
            print(f"   ❌ Error reading inbox log: {e}")
            
        # 4. QUICK STATS
        print()
        print("📈 QUICK STATS:")
        print("-" * 30)
        try:
            cursor.execute("SELECT COUNT(*) FROM subscribers")
            sub_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM reminders")
            rem_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM inbox_log")
            log_count = cursor.fetchone()[0]
            
            print(f"   👤 Total subscribers: {sub_count}")
            print(f"   ⏰ Total reminders: {rem_count}")
            print(f"   📧 Total processed emails: {log_count}")
            
        except Exception as e:
            print(f"   ❌ Error getting stats: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    inspect_database()