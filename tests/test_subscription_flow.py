"""
Test subscription flow: create, update, delete subscribers.
"""
import pytest
from services.subscription_service import (
    add_or_update_subscriber,
    delete_subscriber,
    get_subscriber
)


def test_add_new_subscriber(test_db, mock_geocode):
    """Test adding a new subscriber."""
    add_or_update_subscriber(
        email='new@example.com',
        location='Bratislava, Slovakia',
        lat=48.1486,
        lon=17.1077,
        personality='neutral',
        language='en',
        timezone='Europe/Bratislava',
        db_path=test_db
    )
    
    result = get_subscriber('new@example.com', db_path=test_db)
    assert result is not None
    assert result[0] == 'Bratislava, Slovakia'
    assert result[3] == 'neutral'
    assert result[4] == 'en'


def test_update_existing_subscriber(test_db):
    """Test updating an existing subscriber's location."""
    # Add initial subscriber
    add_or_update_subscriber(
        email='update@example.com',
        location='Bratislava, Slovakia',
        lat=48.1486,
        lon=17.1077,
        personality='neutral',
        language='en',
        timezone='Europe/Bratislava',
        db_path=test_db
    )
    
    # Update subscriber
    add_or_update_subscriber(
        email='update@example.com',
        location='Prague, Czech Republic',
        lat=50.0755,
        lon=14.4378,
        personality='cute',
        language='sk',
        timezone='Europe/Prague',
        db_path=test_db
    )
    
    result = get_subscriber('update@example.com', db_path=test_db)
    assert result[0] == 'Prague, Czech Republic'
    assert result[3] == 'cute'
    assert result[4] == 'sk'


def test_update_personality_only(test_db):
    """Test updating only personality without changing location."""
    # Add initial subscriber
    add_or_update_subscriber(
        email='personality@example.com',
        location='Bratislava, Slovakia',
        lat=48.1486,
        lon=17.1077,
        personality='neutral',
        language='en',
        timezone='Europe/Bratislava',
        db_path=test_db
    )
    
    # Update only personality
    add_or_update_subscriber(
        email='personality@example.com',
        location='Bratislava, Slovakia',
        lat=48.1486,
        lon=17.1077,
        personality='brutal',
        language='en',
        timezone='Europe/Bratislava',
        db_path=test_db
    )
    
    result = get_subscriber('personality@example.com', db_path=test_db)
    assert result[0] == 'Bratislava, Slovakia'
    assert result[3] == 'brutal'


def test_update_language_only(test_db):
    """Test updating only language without changing location."""
    # Add initial subscriber
    add_or_update_subscriber(
        email='language@example.com',
        location='Bratislava, Slovakia',
        lat=48.1486,
        lon=17.1077,
        personality='neutral',
        language='en',
        timezone='Europe/Bratislava',
        db_path=test_db
    )
    
    # Update only language
    add_or_update_subscriber(
        email='language@example.com',
        location='Bratislava, Slovakia',
        lat=48.1486,
        lon=17.1077,
        personality='neutral',
        language='sk',
        timezone='Europe/Bratislava',
        db_path=test_db
    )
    
    result = get_subscriber('language@example.com', db_path=test_db)
    assert result[4] == 'sk'


def test_delete_existing_subscriber(test_db):
    """Test deleting a subscriber."""
    # Add subscriber
    add_or_update_subscriber(
        email='delete@example.com',
        location='Bratislava, Slovakia',
        lat=48.1486,
        lon=17.1077,
        personality='neutral',
        language='en',
        timezone='Europe/Bratislava',
        db_path=test_db
    )
    
    # Delete subscriber
    rowcount = delete_subscriber('delete@example.com', db_path=test_db)
    assert rowcount == 1
    
    # Verify deletion
    result = get_subscriber('delete@example.com', db_path=test_db)
    assert result is None


def test_delete_nonexistent_subscriber(test_db):
    """Test deleting a subscriber that doesn't exist."""
    rowcount = delete_subscriber('nonexistent@example.com', db_path=test_db)
    assert rowcount == 0


def test_get_nonexistent_subscriber(test_db):
    """Test getting a subscriber that doesn't exist."""
    result = get_subscriber('nonexistent@example.com', db_path=test_db)
    assert result is None


def test_multiple_subscribers(test_db):
    """Test adding and managing multiple subscribers."""
    subscribers = [
        ('user1@example.com', 'Bratislava, Slovakia', 48.1486, 17.1077, 'Europe/Bratislava', 'neutral', 'en'),
        ('user2@example.com', 'New York, USA', 40.7128, -74.0060, 'America/New_York', 'cute', 'en'),
        ('user3@example.com', 'Tokyo, Japan', 35.6762, 139.6503, 'Asia/Tokyo', 'brutal', 'en'),
    ]
    
    for email, location, lat, lon, timezone, personality, language in subscribers:
        add_or_update_subscriber(email, location, lat, lon, personality, language, timezone, db_path=test_db)
    
    # Verify all exist
    for email, location, _, _, _, _, _ in subscribers:
        result = get_subscriber(email, db_path=test_db)
        assert result is not None
        assert result[0] == location
