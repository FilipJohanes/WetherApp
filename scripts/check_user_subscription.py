#!/usr/bin/env python3
"""
Check subscription status for a specific user
"""
import os
import sys
import sqlite3

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

def check_user(email):
    """Check user subscription status in database."""
    db_path = os.getenv("APP_DB_PATH", "app.db")
    
    print("=" * 60)
    print(f"Checking subscription for: {email}")
    print(f"Database: {db_path}")
    print("=" * 60)
    print()
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    try:
        # Check users table
        print("📋 USER TABLE:")
        print("-" * 40)
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if user:
            for key in user.keys():
                print(f"  {key}: {user[key]}")
        else:
            print(f"  ❌ User not found in users table")
        print()
        
        # Check weather_subscriptions table
        print("🌤️  WEATHER_SUBSCRIPTIONS TABLE:")
        print("-" * 40)
        weather_sub = conn.execute("SELECT * FROM weather_subscriptions WHERE email = ?", (email,)).fetchone()
        if weather_sub:
            for key in weather_sub.keys():
                print(f"  {key}: {weather_sub[key]}")
        else:
            print(f"  ❌ No weather subscription found")
        print()
        
        # Check with the same JOIN query used by the API
        print("🔍 API QUERY RESULT (with weather_enabled = 1 filter):")
        print("-" * 40)
        api_result = conn.execute("""
            SELECT ws.email, ws.location, ws.lat, ws.lon, 
                   COALESCE(u.timezone, 'UTC') as timezone, 
                   ws.personality, ws.language 
            FROM weather_subscriptions ws
            JOIN users u ON ws.email = u.email
            WHERE ws.email = ? AND u.weather_enabled = 1
        """, (email,)).fetchone()
        if api_result:
            print("  ✅ Subscription would be returned by API:")
            for key in api_result.keys():
                print(f"    {key}: {api_result[key]}")
        else:
            print(f"  ❌ Subscription would NOT be returned by API")
            print(f"     (either no subscription or weather_enabled != 1)")
        print()
        
        # Check email sending query
        print("📧 EMAIL SENDING QUERY RESULT:")
        print("-" * 40)
        email_result = conn.execute("""
            SELECT 
                u.email, 
                ws.lat, 
                ws.lon, 
                u.timezone,
                u.weather_enabled, 
                u.countdown_enabled, 
                u.reminder_enabled,
                ws.location,
                ws.personality,
                ws.language
            FROM users u
            LEFT JOIN weather_subscriptions ws ON u.email = ws.email
            WHERE u.email = ? AND (u.weather_enabled = 1 OR u.countdown_enabled = 1 OR u.reminder_enabled = 1)
        """, (email,)).fetchone()
        if email_result:
            print("  ✅ User would receive emails:")
            for key in email_result.keys():
                print(f"    {key}: {email_result[key]}")
        else:
            print(f"  ❌ User would NOT receive emails")
        
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        email = sys.argv[1]
    else:
        email = "info@bikesport-senec.sk"
    
    check_user(email)
