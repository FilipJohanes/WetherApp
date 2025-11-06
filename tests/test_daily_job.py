#!/usr/bin/env python3
"""Test the daily weather job to verify individual personality sending."""

import sqlite3
from app import run_daily_weather_job

def test_daily_weather_job():
    """Test that daily weather job sends individual personalities."""
    print("=== Testing Daily Weather Job ===\n")
    
    # Clear and setup test subscribers
    conn = sqlite3.connect("app.db")
    conn.execute("DELETE FROM subscribers")
    
    # Add test subscribers with different personalities
    test_subscribers = [
        ("user1@test.com", "London", 51.5074, -0.1278, "cute"),
        ("user2@test.com", "Prague", 50.0755, 14.4378, "brutal"), 
        ("user3@test.com", "Tokyo", 35.6762, 139.6503, "neutral")
    ]
    
    for email, location, lat, lon, personality in test_subscribers:
        conn.execute("""
            INSERT INTO subscribers (email, location, lat, lon, personality, updated_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, (email, location, lat, lon, personality))
    
    conn.commit()
    
    # Verify subscribers were added
    subscribers = conn.execute("SELECT email, location, personality FROM subscribers").fetchall()
    print("Test subscribers added:")
    for sub in subscribers:
        print(f"  {sub[0]} -> {sub[1]} ({sub[2]} mode)")
    print()
    
    conn.close()
    
    # Create dummy config
    class DummyConfig:
        def __init__(self):
            self.timezone = "UTC"
    
    config = DummyConfig()
    
    # Run the daily weather job in dry-run mode
    print("Running daily weather job (dry-run mode)...")
    print("This should generate individual weather reports for each subscriber.")
    print("=" * 60)
    
    run_daily_weather_job(config, dry_run=True)

if __name__ == "__main__":
    test_daily_weather_job()