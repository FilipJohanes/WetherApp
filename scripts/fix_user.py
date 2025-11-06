#!/usr/bin/env python3
"""Fix corrupted location data for specific user"""

import sqlite3

def fix_user_location():
    conn = sqlite3.connect("app.db")
    try:
        # Check current data
        cursor = conn.cursor()
        cursor.execute("SELECT email, location, lat, lon FROM subscribers WHERE email = ?", 
                      ("filip.johanes9@gmail.com",))
        result = cursor.fetchone()
        
        if result:
            print(f"Current data: {result}")
            print("Fixing location data...")
            
            # Update with proper location (you can change this)
            cursor.execute("""
                UPDATE subscribers 
                SET location = ?, lat = ?, lon = ?
                WHERE email = ?
            """, ("Bratislava, Slovakia", 48.1486, 17.1077, "filip.johanes9@gmail.com"))
            
            conn.commit()
            print("✅ Location fixed to Bratislava, Slovakia")
        else:
            print("User not found")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_user_location()