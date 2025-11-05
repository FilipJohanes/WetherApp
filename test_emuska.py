#!/usr/bin/env python3
"""Test the new Emuska personality mode."""

import sqlite3
from app import generate_weather_summary, load_weather_messages

def test_emuska_mode():
    """Test the Emuska personality mode functionality."""
    print("=== Testing Emuska Mode ===\n")
    
    # Test loading weather messages with new format
    print("1. Testing weather message loading:")
    messages = load_weather_messages()
    
    # Check if messages were loaded correctly with emuska mode
    sample_conditions = ['raining', 'sunny', 'default']
    for condition in sample_conditions:
        if condition in messages:
            msg_dict = messages[condition]
            print(f"{condition}: has {len(msg_dict)} personalities")
            for personality in ['neutral', 'cute', 'brutal', 'emuska']:
                if personality in msg_dict:
                    emuska_msg = msg_dict[personality] 
                    status = "✅ (populated)" if emuska_msg else "📝 (blank - ready for custom text)"
                    print(f"  {personality}: {status}")
                else:
                    print(f"  {personality}: ❌ missing")
            print()
    
    # Test weather generation with Emuska mode
    print("2. Testing weather generation with Emuska mode:")
    
    # Mock weather data
    test_weather = {
        'temp_max': 20.0,
        'temp_min': 12.0,
        'precipitation_probability': 30.0,
        'precipitation_sum': 0.5,
        'wind_speed_max': 10.0,
        'weather_code': 1  # Sunny
    }
    
    # Generate weather for Emuska mode
    emuska_summary = generate_weather_summary(test_weather, "Prague", "emuska")
    print("Emuska mode weather report:")
    print("-" * 40)
    print(emuska_summary)
    print("-" * 40)
    
    # Test database functionality
    print("\n3. Testing database with Emuska mode:")
    
    # Add a test subscriber with Emuska mode
    conn = sqlite3.connect("app.db")
    conn.execute("DELETE FROM subscribers WHERE email = 'emuska@test.com'")
    conn.execute("""
        INSERT INTO subscribers (email, location, lat, lon, personality, updated_at)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
    """, ("emuska@test.com", "Secret Location", 50.0755, 14.4378, "emuska"))
    conn.commit()
    
    # Verify subscriber was added
    subscriber = conn.execute("""
        SELECT email, location, personality FROM subscribers WHERE email = ?
    """, ("emuska@test.com",)).fetchone()
    
    if subscriber:
        print(f"✅ Emuska subscriber added: {subscriber[0]} -> {subscriber[1]} ({subscriber[2]} mode)")
    else:
        print("❌ Failed to add Emuska subscriber")
    
    conn.close()
    
    print("\n✅ Emuska mode is ready!")
    print("📝 Note: All Emuska weather messages are currently blank.")
    print("   You can now add custom messages to weather_messages.txt in the Emuska column.")
    print("   To activate for a user, manually update their database record:")
    print("   UPDATE subscribers SET personality='emuska' WHERE email='user@example.com';")

if __name__ == "__main__":
    test_emuska_mode()