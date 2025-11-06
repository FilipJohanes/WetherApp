#!/usr/bin/env python3
"""Add new user to the Daily Brief Service database"""

import sqlite3
from datetime import datetime
import sys
import os

# Add parent directory to path to import app functions
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # Go up one level
from app import geocode_location

def add_user(email, location_str, personality="neutral", language="en"):
    """Add a new user to the subscribers database."""
    
    print(f"🔍 Adding user: {email}")
    print(f"📍 Location: {location_str}")
    print(f"🎭 Personality: {personality}")
    print(f"🌍 Language: {language}")
    print("-" * 40)
    
    # First, geocode the location
    print("🗺️ Geocoding location...")
    coordinates = geocode_location(location_str)
    
    if not coordinates:
        print(f"❌ Failed to geocode location: {location_str}")
        return False
    
    lat, lon, display_name = coordinates
    print(f"✅ Location found: {lat:.4f}, {lon:.4f} ({display_name})")
    
    # Connect to database
    conn = sqlite3.connect("app.db")
    try:
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT email FROM subscribers WHERE email = ?", (email,))
        existing = cursor.fetchone()
        
        if existing:
            print(f"⚠️ User {email} already exists. Updating...")
            cursor.execute("""
                UPDATE subscribers 
                SET location = ?, lat = ?, lon = ?, personality = ?, language = ?, updated_at = ?
                WHERE email = ?
            """, (location_str, lat, lon, personality, language, datetime.now().isoformat(), email))
            action = "Updated"
        else:
            print(f"➕ Adding new user {email}...")
            cursor.execute("""
                INSERT INTO subscribers (email, location, lat, lon, personality, language, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (email, location_str, lat, lon, personality, language, datetime.now().isoformat()))
            action = "Added"
        
        conn.commit()
        print(f"✅ {action} user successfully!")
        
        # Verify the addition
        cursor.execute("SELECT * FROM subscribers WHERE email = ?", (email,))
        user_data = cursor.fetchone()
        
        if user_data:
            print("\n📊 User details:")
            columns = ['email', 'location', 'lat', 'lon', 'updated_at', 'personality', 'language']
            for col, val in zip(columns, user_data):
                print(f"   {col}: {val}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    # Add the specified user
    success = add_user(
        email="em.solarova@gmail.com",
        location_str="Bratislava",
        personality="emuska", 
        language="sk"
    )
    
    if success:
        print("\n🎉 User added successfully!")
        print("📧 They will receive daily weather forecasts at 05:00 local time")
        print("🎭 With emuska personality in Slovak language")
    else:
        print("\n❌ Failed to add user")