"""
End-to-End Test of Unified Database Schema
Demonstrates that all modules work together correctly.
"""
import sqlite3
import os
from datetime import datetime
from zoneinfo import ZoneInfo

# Set test database
os.environ['APP_DB_PATH'] = 'test_unified.db'

from app import init_db
from services.subscription_service import add_or_update_subscriber, delete_subscriber, get_subscriber
from services.countdown_service import add_countdown, get_user_countdowns, delete_countdown, CountdownEvent

DB_PATH = 'test_unified.db'

def cleanup():
    """Remove test database."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

def test_unified_database():
    """Test the complete unified database workflow."""
    print("=" * 70)
    print("UNIFIED DATABASE END-TO-END TEST")
    print("=" * 70)
    
    # Clean start
    cleanup()
    
    # 1. Initialize database
    print("\n1️⃣  Initializing unified database...")
    init_db(DB_PATH)
    print("   ✅ Database initialized")
    
    # 2. Add weather subscription (creates user + enables weather)
    print("\n2️⃣  Adding weather subscription...")
    test_email = "test@unified.com"
    add_or_update_subscriber(
        email=test_email,
        location="Prague, Czech Republic",
        lat=50.0755,
        lon=14.4378,
        personality="cute",
        language="en",
        timezone="Europe/Prague"
    )
    print("   ✅ Weather subscription added")
    
    # 3. Verify user was created with weather enabled
    print("\n3️⃣  Verifying master user table...")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    user = conn.execute("SELECT * FROM users WHERE email = ?", (test_email,)).fetchone()
    assert user is not None, "User should exist"
    assert user['weather_enabled'] == 1, "Weather should be enabled"
    assert user['countdown_enabled'] == 0, "Countdown should not be enabled yet"
    print(f"   ✅ User created: {user['email']}")
    print(f"   ✅ Weather enabled: {bool(user['weather_enabled'])}")
    print(f"   ✅ Countdown enabled: {bool(user['countdown_enabled'])}")
    
    # 4. Verify weather subscription exists
    print("\n4️⃣  Verifying weather subscription...")
    weather = conn.execute("SELECT * FROM weather_subscriptions WHERE email = ?", (test_email,)).fetchone()
    assert weather is not None, "Weather subscription should exist"
    assert weather['location'] == "Prague, Czech Republic"
    assert weather['personality'] == "cute"
    print(f"   ✅ Location: {weather['location']}")
    print(f"   ✅ Personality: {weather['personality']}")
    print(f"   ✅ Language: {weather['language']}")
    conn.close()
    
    # 5. Add countdown (should enable countdown flag)
    print("\n5️⃣  Adding countdown...")
    event = CountdownEvent(
        name="Vacation",
        date="2026-07-01",
        yearly=False,
        email=test_email,
        message_before="Days until vacation: {days}"
    )
    add_countdown(event, DB_PATH)
    print("   ✅ Countdown added")
    
    # 6. Verify countdown flag enabled
    print("\n6️⃣  Verifying countdown module enabled...")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    user = conn.execute("SELECT * FROM users WHERE email = ?", (test_email,)).fetchone()
    assert user['countdown_enabled'] == 1, "Countdown should now be enabled"
    print(f"   ✅ Countdown enabled: {bool(user['countdown_enabled'])}")
    
    # 7. Verify countdown exists
    countdowns = get_user_countdowns(test_email, DB_PATH)
    assert len(countdowns) == 1, "Should have 1 countdown"
    assert countdowns[0].name == "Vacation"
    print(f"   ✅ Countdown found: {countdowns[0].name} on {countdowns[0].date}")
    
    # 8. Test foreign key cascade (delete user should delete all related data)
    print("\n7️⃣  Testing foreign key cascade...")
    weather_count_before = conn.execute("SELECT COUNT(*) FROM weather_subscriptions WHERE email = ?", (test_email,)).fetchone()[0]
    countdown_count_before = conn.execute("SELECT COUNT(*) FROM countdowns WHERE email = ?", (test_email,)).fetchone()[0]
    print(f"   Before delete - Weather subs: {weather_count_before}, Countdowns: {countdown_count_before}")
    conn.close()
    
    # Enable foreign keys and delete user (should cascade)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("DELETE FROM users WHERE email = ?", (test_email,))
    conn.commit()
    
    weather_count_after = conn.execute("SELECT COUNT(*) FROM weather_subscriptions WHERE email = ?", (test_email,)).fetchone()[0]
    countdown_count_after = conn.execute("SELECT COUNT(*) FROM countdowns WHERE email = ?", (test_email,)).fetchone()[0]
    print(f"   After delete - Weather subs: {weather_count_after}, Countdowns: {countdown_count_after}")
    
    assert weather_count_after == 0, "Weather subscription should be deleted"
    assert countdown_count_after == 0, "Countdown should be deleted"
    print("   ✅ CASCADE DELETE works correctly!")
    conn.close()
    
    # 9. Test module disable (add back user, then delete subscription)
    print("\n8️⃣  Testing module disable...")
    add_or_update_subscriber(
        email=test_email,
        location="Prague, Czech Republic",
        lat=50.0755,
        lon=14.4378,
        personality="cute",
        language="en",
        timezone="Europe/Prague"
    )
    
    # Delete weather subscription
    deleted = delete_subscriber(test_email, DB_PATH)
    assert deleted > 0, "Subscription should be deleted"
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    user = conn.execute("SELECT * FROM users WHERE email = ?", (test_email,)).fetchone()
    assert user is not None, "User should still exist"
    assert user['weather_enabled'] == 0, "Weather should be disabled"
    print(f"   ✅ Weather module disabled (flag = {user['weather_enabled']})")
    print("   ✅ User still exists in master table")
    conn.close()
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED - UNIFIED SCHEMA WORKS PERFECTLY!")
    print("=" * 70)
    
    # Cleanup
    cleanup()
    print("\n🧹 Test database cleaned up")

if __name__ == "__main__":
    try:
        test_unified_database()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        cleanup()
        raise
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        cleanup()
        raise
