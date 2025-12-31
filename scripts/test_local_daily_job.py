#!/usr/bin/env python3
"""
Manual test script: Simulate daily weather job execution.
Tests the 05:00 local time email sending logic without real IMAP/SMTP.
"""
import os
import sys
import sqlite3
import tempfile
from datetime import datetime
from zoneinfo import ZoneInfo
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import init_db, Config

from services.email_service import run_daily_job


def mock_send_email(config, to, subject, body):
    """Mock email sender that prints instead of sending."""
    print(f"\n{'='*60}")
    print(f"📧 SIMULATED EMAIL")
    print(f"{'='*60}")
    print(f"To: {to}")
    print(f"Subject: {subject}")
    print(f"{'='*60}")
    print(body)
    print(f"{'='*60}\n")
    return True


def mock_weather_forecast(lat, lon, timezone_str):
    """Mock weather forecast with realistic data."""
    return {
        'temp_max': 18.5,
        'temp_min': 8.2,
        'precipitation_sum': 1.5,
        'precipitation_probability': 35,
        'wind_speed_max': 12.0,
    }


def setup_test_database():
    """Create temporary test database with sample subscribers."""
    fd, db_path = tempfile.mkstemp(suffix='_test.db')
    os.close(fd)
    
    print(f"🗄️  Creating test database: {db_path}")
    
    # Initialize schema
    init_db(db_path)
    
    # Insert test subscribers in different timezones
    conn = sqlite3.connect(db_path)
    
    test_subscribers = [
        ('bratislava@test.com', 'Bratislava, Slovakia', 48.1486, 17.1077, 'Europe/Bratislava', 'neutral', 'en'),
        ('newyork@test.com', 'New York, USA', 40.7128, -74.0060, 'America/New_York', 'cute', 'en'),
        ('tokyo@test.com', 'Tokyo, Japan', 35.6762, 139.6503, 'Asia/Tokyo', 'brutal', 'en'),
        ('london@test.com', 'London, UK', 51.5074, -0.1278, 'Europe/London', 'neutral', 'en'),
    ]
    
    for email, location, lat, lon, timezone, personality, language in test_subscribers:
        conn.execute("""
            INSERT INTO subscribers (email, location, lat, lon, timezone, personality, language, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (email, location, lat, lon, timezone, personality, language, datetime.now().isoformat()))
        print(f"  ✅ Added subscriber: {email} ({timezone})")
    
    conn.commit()
    conn.close()
    
    return db_path


def simulate_daily_job(test_time_str='05:00', timezone_str='Europe/Bratislava'):
    """Simulate running the daily job at a specific time."""
    print(f"\n{'='*60}")
    print(f"🕐 SIMULATING DAILY JOB")
    print(f"{'='*60}")
    print(f"Simulated time: {test_time_str} {timezone_str}")
    print(f"{'='*60}\n")
    
    # Create test database
    db_path = setup_test_database()
    
    # Set test database path
    os.environ['APP_DB_PATH'] = db_path
    
    # Create mock config
    mock_config = Mock(spec=Config)
    mock_config.email_address = "dailybrief@test.com"
    mock_config.email_password = "test_pass"
    mock_config.smtp_host = "smtp.test.com"
    mock_config.smtp_port = 587
    mock_config.smtp_use_tls = True
    mock_config.timezone = timezone_str
    mock_config.language = "en"
    
    # Parse test time
    hour, minute = map(int, test_time_str.split(':'))
    test_datetime = datetime(2025, 12, 16, hour, minute, 0, tzinfo=ZoneInfo(timezone_str))
    
    # Mock external dependencies
    with patch('services.email_service.send_email', side_effect=mock_send_email):
        with patch('services.weather_service.get_weather_forecast', side_effect=mock_weather_forecast):
            with patch('services.email_service.datetime') as mock_dt:
                # Mock datetime.now to return test time
                def mock_now(tz=None):
                    if tz:
                        return test_datetime.astimezone(tz)
                    return test_datetime
                
                mock_dt.now = mock_now
                mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
                
                print("🚀 Running daily job...\n")
                run_daily_job(mock_config, db_path=db_path)
    
    # Cleanup
    os.unlink(db_path)
    print("\n✅ Simulation complete!")
    print(f"{'='*60}\n")


def main():
    """Run daily job simulation scenarios."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║           Daily Weather Job Test Script                     ║
║           Simulates 05:00 local time email sending          ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    scenarios = [
        ("05:00", "Europe/Bratislava", "Bratislava 5 AM - Should send"),
        ("15:00", "Europe/Bratislava", "Bratislava 3 PM - Should NOT send"),
        ("05:00", "America/New_York", "New York 5 AM - Should send"),
        ("05:00", "Asia/Tokyo", "Tokyo 5 AM - Should send"),
    ]
    
    for i, (time_str, tz, description) in enumerate(scenarios, 1):
        print(f"\n📋 Scenario {i}/{len(scenarios)}: {description}")
        input("Press Enter to run this scenario...")
        simulate_daily_job(time_str, tz)
    
    print("\n🎉 All scenarios complete!")


if __name__ == '__main__':
    main()
