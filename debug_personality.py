#!/usr/bin/env python3
"""Debug personality mode functionality."""

import sqlite3
from app import parse_plaintext, handle_weather_command, generate_weather_summary, Config

def test_personality_workflow():
    """Test the complete personality workflow."""
    print("=== Testing Personality Workflow ===\n")
    
    # Test parsing
    print("1. Testing email parsing:")
    test_emails = [
        "London\npersonality=cute",
        "Prague\npersonality=brutal", 
        "personality=neutral\nNew York",
        "Tokyo"  # No personality specified
    ]
    
    for email_body in test_emails:
        result = parse_plaintext(email_body)
        print(f"Input: {email_body!r}")
        print(f"Parsed: {result}")
        print()
    
    # Test database operations
    print("2. Testing database operations:")
    
    # Clear existing subscribers for clean test
    conn = sqlite3.connect("app.db")
    conn.execute("DELETE FROM subscribers")
    conn.commit()
    conn.close()
    
    # Create dummy config
    class DummyConfig:
        def __init__(self):
            self.timezone = "UTC"
    
    config = DummyConfig()
    
    # Test subscription with personality directly to database
    print("Subscribing test@example.com to London with cute personality...")
    
    # Simulate handle_weather_command logic without email sending
    from datetime import datetime
    from zoneinfo import ZoneInfo
    
    conn = sqlite3.connect("app.db")
    conn.execute("""
        INSERT OR REPLACE INTO subscribers (email, location, lat, lon, updated_at, personality)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ("test@example.com", "London", 51.5074, -0.1278, datetime.now().isoformat(), "cute"))
    conn.commit()
    conn.close()
    
    # Check database
    conn = sqlite3.connect("app.db")
    subscriber = conn.execute("SELECT email, location, personality FROM subscribers WHERE email = ?", ("test@example.com",)).fetchone()
    if subscriber:
        print(f"Database entry: {subscriber}")
    else:
        print("No subscriber found in database!")
    conn.close()
    
    # Test weather generation
    print("\n3. Testing weather message generation:")
    
    # Mock weather data
    test_weather = {
        'temp_max': 15.0,
        'temp_min': 8.0,
        'precipitation_probability': 60.0,
        'precipitation_sum': 2.5,
        'wind_speed_max': 15.0,
        'weather_code': 61  # Light rain
    }
    
    for personality in ['neutral', 'cute', 'brutal']:
        print(f"\nPersonality: {personality}")
        summary = generate_weather_summary(test_weather, "London", personality)
        print(summary[:200] + "..." if len(summary) > 200 else summary)
        print("-" * 50)

if __name__ == "__main__":
    test_personality_workflow()