#!/usr/bin/env python3
"""
Comprehensive Database Operations Tests
Tests all database functions to ensure schema consistency
"""
import pytest
import sqlite3
import os
import tempfile
from datetime import datetime

# Add parent directory to path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.user_service import register_user, authenticate_user, get_user_by_email, hash_password
from services.subscription_service import add_or_update_subscriber, delete_subscriber, get_subscriber
from services.countdown_service import add_countdown, get_user_countdowns, delete_countdown, CountdownEvent


@pytest.fixture
def test_db():
    """Create a temporary test database."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # Initialize database with correct schema
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")
    
    # Create users table (correct schema without lat/lon)
    conn.execute("""
        CREATE TABLE users (
            email TEXT PRIMARY KEY,
            username TEXT,
            nickname TEXT,
            password_hash TEXT,
            timezone TEXT DEFAULT 'UTC',
            subscription_type TEXT DEFAULT 'free',
            weather_enabled INTEGER DEFAULT 0,
            countdown_enabled INTEGER DEFAULT 0,
            reminder_enabled INTEGER DEFAULT 0,
            email_consent INTEGER DEFAULT 0,
            terms_accepted INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    
    # Create weather_subscriptions table (with lat/lon)
    conn.execute("""
        CREATE TABLE weather_subscriptions (
            email TEXT PRIMARY KEY,
            location TEXT NOT NULL,
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            personality TEXT DEFAULT 'neutral',
            language TEXT DEFAULT 'en',
            last_sent_date TEXT,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE
        )
    """)
    
    # Create countdowns table
    conn.execute("""
        CREATE TABLE countdowns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            yearly INTEGER DEFAULT 0,
            message_before TEXT,
            message_after TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()
    
    # Set environment variable to use test database
    original_db = os.environ.get('APP_DB_PATH')
    os.environ['APP_DB_PATH'] = path
    
    yield path
    
    # Cleanup
    if original_db:
        os.environ['APP_DB_PATH'] = original_db
    else:
        os.environ.pop('APP_DB_PATH', None)
    
    try:
        os.unlink(path)
    except:
        pass


class TestUserService:
    """Test user service database operations."""
    
    def test_register_user_success(self, test_db):
        """Test successful user registration."""
        success, message = register_user(
            email='test@example.com',
            password='password123',
            nickname='TestUser',
            username='testuser',
            email_consent=True,
            terms_accepted=True
        )
        
        assert success is True
        assert 'successful' in message.lower()
        
        # Verify user was created with correct columns
        conn = sqlite3.connect(test_db)
        conn.row_factory = sqlite3.Row
        user = conn.execute("SELECT * FROM users WHERE email = ?", ('test@example.com',)).fetchone()
        conn.close()
        
        assert user is not None
        assert user['email'] == 'test@example.com'
        assert user['nickname'] == 'TestUser'
        assert user['username'] == 'testuser'
        assert user['email_consent'] == 1
        assert user['terms_accepted'] == 1
        assert user['weather_enabled'] == 0
        assert user['countdown_enabled'] == 0
        assert user['password_hash'] is not None
        # Ensure no lat/lon columns exist
        assert 'lat' not in user.keys()
        assert 'lon' not in user.keys()
    
    def test_register_user_duplicate(self, test_db):
        """Test registering duplicate user fails."""
        register_user('duplicate@example.com', 'password123')
        success, message = register_user('duplicate@example.com', 'password123')
        
        assert success is False
        assert 'already registered' in message.lower()
    
    def test_authenticate_user_success(self, test_db):
        """Test successful authentication."""
        register_user('auth@example.com', 'mypassword', nickname='AuthUser')
        user = authenticate_user('auth@example.com', 'mypassword')
        
        assert user is not None
        assert user['email'] == 'auth@example.com'
        assert user['nickname'] == 'AuthUser'
        assert 'password_hash' not in user  # Should not expose password hash
    
    def test_authenticate_user_wrong_password(self, test_db):
        """Test authentication with wrong password fails."""
        register_user('wrong@example.com', 'correctpassword')
        user = authenticate_user('wrong@example.com', 'wrongpassword')
        
        assert user is None
    
    def test_authenticate_user_nonexistent(self, test_db):
        """Test authentication with non-existent user fails."""
        user = authenticate_user('nonexistent@example.com', 'password')
        
        assert user is None
    
    def test_get_user_by_email_success(self, test_db):
        """Test getting user by email."""
        register_user('getuser@example.com', 'password', nickname='GetUser')
        user = get_user_by_email('getuser@example.com')
        
        assert user is not None
        assert user['email'] == 'getuser@example.com'
        assert user['nickname'] == 'GetUser'
        assert user['timezone'] == 'UTC'
        assert user['subscription_type'] == 'free'
        assert 'password_hash' not in user
    
    def test_get_user_by_email_nonexistent(self, test_db):
        """Test getting non-existent user returns None."""
        user = get_user_by_email('nonexistent@example.com')
        
        assert user is None


class TestSubscriptionService:
    """Test subscription service database operations."""
    
    def test_add_subscriber_new_user(self, test_db):
        """Test adding subscription for new user (creates user)."""
        add_or_update_subscriber(
            email='newsubscriber@example.com',
            location='Bratislava, Slovakia',
            lat=48.1486,
            lon=17.1077,
            personality='friendly',
            language='en',
            timezone='Europe/Bratislava',
            db_path=test_db
        )
        
        # Verify user was created
        conn = sqlite3.connect(test_db)
        conn.row_factory = sqlite3.Row
        user = conn.execute("SELECT * FROM users WHERE email = ?", ('newsubscriber@example.com',)).fetchone()
        
        assert user is not None
        assert user['email'] == 'newsubscriber@example.com'
        assert user['weather_enabled'] == 1
        assert user['timezone'] == 'Europe/Bratislava'
        # Verify no lat/lon in users table
        assert 'lat' not in user.keys()
        assert 'lon' not in user.keys()
        
        # Verify weather subscription was created with lat/lon
        ws = conn.execute("SELECT * FROM weather_subscriptions WHERE email = ?", ('newsubscriber@example.com',)).fetchone()
        
        assert ws is not None
        assert ws['location'] == 'Bratislava, Slovakia'
        assert ws['lat'] == 48.1486
        assert ws['lon'] == 17.1077
        assert ws['personality'] == 'friendly'
        assert ws['language'] == 'en'
        
        conn.close()
    
    def test_add_subscriber_existing_user(self, test_db):
        """Test adding subscription for existing user."""
        # Register user first
        register_user('existing@example.com', 'password')
        
        # Add weather subscription
        add_or_update_subscriber(
            email='existing@example.com',
            location='Prague, Czech Republic',
            lat=50.0755,
            lon=14.4378,
            personality='neutral',
            language='cz',
            timezone='Europe/Prague',
            db_path=test_db
        )
        
        # Verify user's weather_enabled was set to 1
        conn = sqlite3.connect(test_db)
        conn.row_factory = sqlite3.Row
        user = conn.execute("SELECT * FROM users WHERE email = ?", ('existing@example.com',)).fetchone()
        
        assert user['weather_enabled'] == 1
        assert user['timezone'] == 'Europe/Prague'
        
        # Verify subscription
        ws = conn.execute("SELECT * FROM weather_subscriptions WHERE email = ?", ('existing@example.com',)).fetchone()
        
        assert ws is not None
        assert ws['lat'] == 50.0755
        assert ws['lon'] == 14.4378
        
        conn.close()
    
    def test_update_subscriber(self, test_db):
        """Test updating existing subscription."""
        # Add initial subscription
        add_or_update_subscriber(
            email='update@example.com',
            location='Bratislava',
            lat=48.1486,
            lon=17.1077,
            personality='neutral',
            language='sk',
            timezone='Europe/Bratislava',
            db_path=test_db
        )
        
        # Update subscription
        add_or_update_subscriber(
            email='update@example.com',
            location='Vienna, Austria',
            lat=48.2082,
            lon=16.3738,
            personality='funny',
            language='en',
            timezone='Europe/Vienna',
            db_path=test_db
        )
        
        # Verify updated data
        conn = sqlite3.connect(test_db)
        conn.row_factory = sqlite3.Row
        ws = conn.execute("SELECT * FROM weather_subscriptions WHERE email = ?", ('update@example.com',)).fetchone()
        
        assert ws['location'] == 'Vienna, Austria'
        assert ws['lat'] == 48.2082
        assert ws['lon'] == 16.3738
        assert ws['personality'] == 'funny'
        assert ws['language'] == 'en'
        
        conn.close()
    
    def test_get_subscriber(self, test_db):
        """Test getting subscriber information."""
        add_or_update_subscriber(
            email='getsubscriber@example.com',
            location='Budapest',
            lat=47.4979,
            lon=19.0402,
            personality='cute',
            language='hu',
            timezone='Europe/Budapest',
            db_path=test_db
        )
        
        subscriber = get_subscriber('getsubscriber@example.com', db_path=test_db)
        
        assert subscriber is not None
        assert subscriber['location'] == 'Budapest'
        assert subscriber['lat'] == 47.4979  # Should get from ws table
        assert subscriber['lon'] == 19.0402  # Should get from ws table
        assert subscriber['personality'] == 'cute'
        assert subscriber['language'] == 'hu'
        assert subscriber['timezone'] == 'Europe/Budapest'
    
    def test_delete_subscriber(self, test_db):
        """Test deleting subscriber."""
        # Add subscription
        add_or_update_subscriber(
            email='delete@example.com',
            location='Bratislava',
            lat=48.1486,
            lon=17.1077,
            personality='neutral',
            language='sk',
            timezone='Europe/Bratislava',
            db_path=test_db
        )
        
        # Delete subscription
        deleted = delete_subscriber('delete@example.com', db_path=test_db)
        
        assert deleted == 1
        
        # Verify subscription is gone
        subscriber = get_subscriber('delete@example.com', db_path=test_db)
        assert subscriber is None
        
        # Verify weather_enabled was set to 0
        conn = sqlite3.connect(test_db)
        conn.row_factory = sqlite3.Row
        user = conn.execute("SELECT weather_enabled FROM users WHERE email = ?", ('delete@example.com',)).fetchone()
        
        assert user['weather_enabled'] == 0
        
        conn.close()


class TestCountdownService:
    """Test countdown service database operations."""
    
    def test_add_countdown_new_user(self, test_db):
        """Test adding countdown for new user (creates user)."""
        event = CountdownEvent(
            'Birthday',
            '2026-06-15',
            True,
            'countdown@example.com',
            'Birthday coming up!',
            'Happy Birthday!'
        )
        
        add_countdown(event, path=test_db)
        
        # Verify user was created
        conn = sqlite3.connect(test_db)
        conn.row_factory = sqlite3.Row
        user = conn.execute("SELECT * FROM users WHERE email = ?", ('countdown@example.com',)).fetchone()
        
        assert user is not None
        assert user['countdown_enabled'] == 1
        # Verify no lat/lon columns
        assert 'lat' not in user.keys()
        assert 'lon' not in user.keys()
        
        # Verify countdown was created
        countdown = conn.execute("SELECT * FROM countdowns WHERE email = ?", ('countdown@example.com',)).fetchone()
        
        assert countdown is not None
        assert countdown['name'] == 'Birthday'
        assert countdown['date'] == '2026-06-15'
        assert countdown['yearly'] == 1
        assert countdown['message_before'] == 'Birthday coming up!'
        assert countdown['message_after'] == 'Happy Birthday!'
        
        conn.close()
    
    def test_add_countdown_existing_user(self, test_db):
        """Test adding countdown for existing user."""
        # Register user first
        register_user('existingcountdown@example.com', 'password')
        
        event = CountdownEvent(
            'Anniversary',
            '2026-12-25',
            False,
            'existingcountdown@example.com',
            'Anniversary approaching',
            'Happy Anniversary!'
        )
        
        add_countdown(event, path=test_db)
        
        # Verify countdown_enabled was set
        conn = sqlite3.connect(test_db)
        conn.row_factory = sqlite3.Row
        user = conn.execute("SELECT countdown_enabled FROM users WHERE email = ?", ('existingcountdown@example.com',)).fetchone()
        
        assert user['countdown_enabled'] == 1
        
        conn.close()
    
    def test_get_user_countdowns(self, test_db):
        """Test retrieving user's countdowns."""
        email = 'multicount@example.com'
        
        # Add multiple countdowns (note: CountdownEvent constructor is name, date, yearly, email, message_before, message_after)
        events = [
            CountdownEvent('Event 1', '2026-03-01', False, email, 'Before 1', 'After 1'),
            CountdownEvent('Event 2', '2026-04-01', True, email, 'Before 2', 'After 2'),
            CountdownEvent('Event 3', '2026-05-01', False, email, 'Before 3', 'After 3'),
        ]
        
        for event in events:
            add_countdown(event, path=test_db)
        
        # Retrieve countdowns
        countdowns = get_user_countdowns(email, path=test_db)
        
        assert len(countdowns) == 3
        assert all(isinstance(c, CountdownEvent) for c in countdowns)
        assert countdowns[0].name == 'Event 1'
        assert countdowns[1].yearly is True
        assert countdowns[2].message_after == 'After 3'
    
    def test_delete_countdown(self, test_db):
        """Test deleting a countdown."""
        email = 'deletecount@example.com'
        event = CountdownEvent(
            'Deletable Event',
            '2026-07-01',
            False,
            email,
            'Before',
            'After'
        )
        
        add_countdown(event, path=test_db)
        
        # Delete countdown using email and name
        delete_countdown(email, 'Deletable Event', path=test_db)
        
        # Verify deletion
        countdowns = get_user_countdowns(email, path=test_db)
        assert len(countdowns) == 0
    
    def test_delete_last_countdown_disables_module(self, test_db):
        """Test that deleting last countdown disables countdown module."""
        email = 'lastcount@example.com'
        event = CountdownEvent(
            'Last Event',
            '2026-08-01',
            False,
            email,
            'Before',
            'After'
        )
        
        add_countdown(event, path=test_db)
        
        # Delete countdown using email and name
        delete_countdown(email, 'Last Event', path=test_db)
        
        # Verify countdown_enabled was set to 0
        conn = sqlite3.connect(test_db)
        conn.row_factory = sqlite3.Row
        user = conn.execute("SELECT countdown_enabled FROM users WHERE email = ?", (email,)).fetchone()
        
        assert user['countdown_enabled'] == 0
        
        conn.close()


class TestDatabaseIntegrity:
    """Test database integrity and constraints."""
    
    def test_foreign_key_cascade_delete_weather(self, test_db):
        """Test that deleting user cascades to weather_subscriptions."""
        # Add subscription
        add_or_update_subscriber(
            email='cascade@example.com',
            location='Test',
            lat=50.0,
            lon=14.0,
            personality='neutral',
            language='en',
            timezone='UTC',
            db_path=test_db
        )
        
        # Delete user
        conn = sqlite3.connect(test_db)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("DELETE FROM users WHERE email = ?", ('cascade@example.com',))
        conn.commit()
        
        # Verify weather subscription was also deleted
        ws = conn.execute("SELECT * FROM weather_subscriptions WHERE email = ?", ('cascade@example.com',)).fetchone()
        
        assert ws is None
        
        conn.close()
    
    def test_foreign_key_cascade_delete_countdowns(self, test_db):
        """Test that deleting user cascades to countdowns."""
        # Add countdown
        event = CountdownEvent(
            'Test',
            '2026-01-01',
            False,
            'cascadecount@example.com',
            'Before',
            'After'
        )
        add_countdown(event, path=test_db)
        
        # Delete user
        conn = sqlite3.connect(test_db)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("DELETE FROM users WHERE email = ?", ('cascadecount@example.com',))
        conn.commit()
        
        # Verify countdown was also deleted
        countdown = conn.execute("SELECT * FROM countdowns WHERE email = ?", ('cascadecount@example.com',)).fetchone()
        
        assert countdown is None
        
        conn.close()
    
    def test_users_table_has_no_lat_lon(self, test_db):
        """Verify users table doesn't have lat/lon columns."""
        conn = sqlite3.connect(test_db)
        cursor = conn.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        conn.close()
        
        assert 'lat' not in columns
        assert 'lon' not in columns
        assert 'email' in columns
        assert 'timezone' in columns
    
    def test_weather_subscriptions_has_lat_lon(self, test_db):
        """Verify weather_subscriptions table has lat/lon columns."""
        conn = sqlite3.connect(test_db)
        cursor = conn.execute("PRAGMA table_info(weather_subscriptions)")
        columns = [row[1] for row in cursor.fetchall()]
        conn.close()
        
        assert 'lat' in columns
        assert 'lon' in columns
        assert 'location' in columns
        assert 'personality' in columns
        assert 'language' in columns


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
