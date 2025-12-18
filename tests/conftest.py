"""
Pytest configuration and shared fixtures for testing.
Provides test database isolation, mocked external services, and test utilities.
"""
import os
import sys
import pytest
import sqlite3
import tempfile
from datetime import datetime
from zoneinfo import ZoneInfo
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import init_db, Config


@pytest.fixture(scope='function')
def test_db():
    """Create a temporary test database with unified schema initialized."""
    # Create temporary database file
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # Set environment variable for test database
    old_db_path = os.environ.get('APP_DB_PATH')
    os.environ['APP_DB_PATH'] = db_path
    
    # Initialize unified schema (includes all tables)
    init_db(db_path)
    
    yield db_path
    
    # Cleanup
    if old_db_path:
        os.environ['APP_DB_PATH'] = old_db_path
    else:
        os.environ.pop('APP_DB_PATH', None)
    
    try:
        os.unlink(db_path)
    except:
        pass


@pytest.fixture(scope='function')
def db_connection(test_db):
    """Provide a database connection to test database."""
    conn = sqlite3.connect(test_db)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


@pytest.fixture
def config():
    """Real Config object for integration tests."""
    return Config()


@pytest.fixture
def mock_config():
    """Mock Config object with test credentials."""
    config = Mock(spec=Config)
    config.email_address = "test@example.com"
    config.email_password = "test_password"
    config.imap_host = "imap.example.com"
    config.imap_port = 993
    config.smtp_host = "smtp.example.com"
    config.smtp_port = 587
    config.smtp_use_tls = True
    config.timezone = "Europe/Bratislava"
    config.language = "en"
    return config


@pytest.fixture
def mock_geocode():
    """Mock geocode_location to return predictable test data."""
    def mock_geocode_fn(location):
        # Map test locations to specific coordinates
        location_map = {
            "Bratislava, Slovakia": (48.1486, 17.1077, "Bratislava, Slovakia", "Europe/Bratislava"),
            "New York, USA": (40.7128, -74.0060, "New York, USA", "America/New_York"),
            "Tokyo, Japan": (35.6762, 139.6503, "Tokyo, Japan", "Asia/Tokyo"),
            "London, UK": (51.5074, -0.1278, "London, UK", "Europe/London"),
            "Invalid Location": None,
        }
        return location_map.get(location, (50.0, 14.0, location, "UTC"))
    
    with patch('services.weather_service.geocode_location', side_effect=mock_geocode_fn):
        yield mock_geocode_fn


@pytest.fixture
def mock_weather_forecast():
    """Mock get_weather_forecast to return predictable weather data."""
    def mock_forecast_fn(lat, lon, timezone_str):
        # Return consistent weather data for testing
        return {
            'temp_max': 22.5,
            'temp_min': 12.3,
            'precipitation_sum': 2.5,
            'precipitation_probability': 40,
            'wind_speed_max': 15.0,
        }
    
    with patch('services.weather_service.get_weather_forecast', side_effect=mock_forecast_fn):
        yield mock_forecast_fn


@pytest.fixture
def mock_send_email():
    """Mock send_email to capture outgoing emails without actually sending."""
    sent_emails = []
    
    def mock_send_fn(config, to, subject, body):
        sent_emails.append({
            'to': to,
            'subject': subject,
            'body': body,
            'timestamp': datetime.now()
        })
        return True
    
    with patch('services.email_service.send_email', side_effect=mock_send_fn):
        yield sent_emails


@pytest.fixture
def mock_datetime():
    """Mock datetime.now to return fixed time for testing time-dependent logic."""
    def mock_now_fn(tz=None):
        # Default: 5:00 AM Bratislava time on 2025-12-16
        if tz:
            return datetime(2025, 12, 16, 5, 0, 0, tzinfo=tz)
        return datetime(2025, 12, 16, 5, 0, 0, tzinfo=ZoneInfo("Europe/Bratislava"))
    
    with patch('services.email_service.datetime') as mock_dt:
        mock_dt.now = mock_now_fn
        mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
        yield mock_dt


@pytest.fixture
def flask_test_client(test_db):
    """Provide Flask test client with CSRF disabled."""
    os.environ['APP_DB_PATH'] = test_db
    from web_app import app
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_subscriber_data():
    """Provide sample subscriber data for tests."""
    return {
        'email': 'test@example.com',
        'location': 'Bratislava, Slovakia',
        'lat': 48.1486,
        'lon': 17.1077,
        'timezone': 'Europe/Bratislava',
        'personality': 'neutral',
        'language': 'en'
    }


@pytest.fixture
def sample_countdown_data():
    """Provide sample countdown event data for tests."""
    return {
        'email': 'test@example.com',
        'name': 'Test Event',
        'date': '2025-12-25',
        'yearly': False,
        'message_before': 'Event in {days} days',
        'message_after': 'Event was {days} days ago'
    }


# Helper function to insert test data
def insert_subscriber(db_path, email, location, lat, lon, timezone, personality='neutral', language='en', last_sent_date=None):
    """Helper to insert a subscriber into test database."""
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("""
            INSERT INTO subscribers (email, location, lat, lon, timezone, personality, language, updated_at, last_sent_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (email, location, lat, lon, timezone, personality, language, datetime.now().isoformat(), last_sent_date))
        conn.commit()
    finally:
        conn.close()
