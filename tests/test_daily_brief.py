"""
Test suite for Daily Brief Service

This module contains unit tests for all major components.
Safe to commit for cross-PC development.
"""

import pytest
import sqlite3
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from zoneinfo import ZoneInfo

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import (
    parse_plaintext, 
    detect_weather_condition,
    get_weather_message,
    load_weather_messages,
    init_db,
    Config
)


class TestEmailParsing:
    """Test email body parsing functionality."""
    
    def test_delete_command(self):
        """Test DELETE command parsing."""
        result = parse_plaintext("delete")
        assert result == {'command': 'DELETE'}
        
        result = parse_plaintext("DELETE")
        assert result == {'command': 'DELETE'}
        
        result = parse_plaintext("  delete  ")
        assert result == {'command': 'DELETE'}

    def test_personality_commands(self):
        """Test personality mode parsing."""
        for mode in ['neutral', 'cute', 'brutal']:
            result = parse_plaintext(mode)
            assert result == {'command': 'PERSONALITY', 'mode': mode}
            
            # Test case insensitive
            result = parse_plaintext(mode.upper())
            assert result == {'command': 'PERSONALITY', 'mode': mode.lower()}

    def test_weather_location(self):
        """Test location parsing for weather."""
        result = parse_plaintext("Bratislava")
        assert result == {'command': 'WEATHER', 'location': 'Bratislava'}
        
        result = parse_plaintext("Prague, Czech Republic")
        assert result == {'command': 'WEATHER', 'location': 'Prague, Czech Republic'}

    def test_calendar_command(self):
        """Test calendar reminder parsing."""
        body = "date=2025-12-01\ntime=08:30\nmessage=Doctor Appointment\nrepeat=3"
        result = parse_plaintext(body)
        
        expected = {
            'command': 'CALENDAR',
            'date': '2025-12-01',
            'time': '08:30', 
            'message': 'Doctor Appointment',
            'repeat': '3'
        }
        assert result == expected

    def test_weather_with_personality(self):
        """Test weather command with personality setting."""
        body = "Prague\npersonality=cute"
        result = parse_plaintext(body)
        
        expected = {
            'command': 'WEATHER',
            'location': 'Prague',
            'personality': 'cute'
        }
        assert result == expected


class TestWeatherConditions:
    """Test weather condition detection."""

    def test_hot_weather(self):
        """Test hot weather detection."""
        weather = {
            'temp_max': 35, 'temp_min': 25, 
            'precipitation_probability': 10, 'precipitation_sum': 0, 
            'wind_speed_max': 15
        }
        condition = detect_weather_condition(weather)
        assert condition == 'sunny_hot'

    def test_rainy_weather(self):
        """Test rainy weather detection.""" 
        weather = {
            'temp_max': 20, 'temp_min': 15,
            'precipitation_probability': 80, 'precipitation_sum': 10,
            'wind_speed_max': 20
        }
        condition = detect_weather_condition(weather)
        assert condition == 'raining'

    def test_cold_weather(self):
        """Test cold weather detection."""
        weather = {
            'temp_max': 2, 'temp_min': -3,
            'precipitation_probability': 20, 'precipitation_sum': 0,
            'wind_speed_max': 25
        }
        condition = detect_weather_condition(weather)
        assert condition == 'cold'

    def test_snowy_weather(self):
        """Test snowy weather detection."""
        weather = {
            'temp_max': -2, 'temp_min': -8,
            'precipitation_probability': 70, 'precipitation_sum': 15,
            'wind_speed_max': 30
        }
        condition = detect_weather_condition(weather)
        assert condition == 'snowing'


class TestWeatherMessages:
    """Test weather message system."""

    def test_load_default_messages(self):
        """Test loading default messages when file doesn't exist."""
        with patch('os.path.exists', return_value=False):
            messages = load_weather_messages('nonexistent.txt')
            assert 'default' in messages
            assert 'neutral' in messages['default']
            assert 'cute' in messages['default']
            assert 'brutal' in messages['default']

    def test_get_weather_message(self):
        """Test getting weather messages by personality."""
        messages = {
            'raining': {
                'neutral': 'Take an umbrella',
                'cute': 'Cute umbrella time! ☂️',
                'brutal': 'Umbrella or get wet'
            },
            'default': {
                'neutral': 'Check conditions',
                'cute': 'Have a great day! 💖',
                'brutal': 'Weather is weather'
            }
        }
        
        # Test existing condition
        assert get_weather_message('raining', 'cute', messages) == 'Cute umbrella time! ☂️'
        
        # Test fallback to default
        assert get_weather_message('unknown_condition', 'neutral', messages) == 'Check conditions'
        
        # Test invalid personality fallback
        assert get_weather_message('raining', 'invalid', messages) == 'Take an umbrella'


class TestDatabase:
    """Test database operations."""

    def test_database_initialization(self):
        """Test database creation and schema."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            init_db(tmp_path)
            
            # Verify tables exist
            conn = sqlite3.connect(tmp_path)
            cursor = conn.cursor()
            
            # Check subscribers table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='subscribers'")
            assert cursor.fetchone() is not None
            
            # Check reminders table  
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reminders'")
            assert cursor.fetchone() is not None
            
            # Check inbox_log table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='inbox_log'")
            assert cursor.fetchone() is not None
            
            # Check personality column exists
            cursor.execute("PRAGMA table_info(subscribers)")
            columns = [row[1] for row in cursor.fetchall()]
            assert 'personality' in columns
            
            conn.close()
            
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


class TestConfiguration:
    """Test configuration handling."""

    @patch.dict(os.environ, {
        'EMAIL_ADDRESS': 'test@example.com',
        'EMAIL_PASSWORD': 'test_password',
        'IMAP_HOST': 'imap.test.com',
        'SMTP_HOST': 'smtp.test.com',
        'TZ': 'UTC'
    })
    def test_config_loading(self):
        """Test configuration loading from environment."""
        config = Config()
        assert config.email_address == 'test@example.com'
        assert config.email_password == 'test_password'
        assert config.imap_host == 'imap.test.com'
        assert config.smtp_host == 'smtp.test.com'
        assert config.timezone == 'UTC'

    def test_missing_required_config(self):
        """Test handling of missing required configuration."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(SystemExit):
                Config()


if __name__ == '__main__':
    # Run tests when script is executed directly
    pytest.main([__file__, '-v'])