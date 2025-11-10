#!/usr/bin/env python3
"""
Daily Brief Service - Email-driven weather subscriptions.
Copyright (c) 2025 Filip Johanes. All Rights Reserved.

PROPRIETARY SOFTWARE - DO NOT DISTRIBUTE
This software contains proprietary algorithms and unique features including
Slovak "emuska" personality mode. Commercial use or redistribution prohibited.

This service monitors an email inbox for commands and provides:
1. Daily weather digest subscriptions (send location to subscribe)
2. Multi-language support (EN/ES/SK) and personality modes
3. Smart email parsing with system email filtering

Features:
- Weather forecasts at 05:00 local time
- 4 personality modes: neutral, cute, brutal, emuska
- Unicode-safe logging for international users
- Webhook architecture for scalability

Requirements:
- Python 3.11+
- See requirements.txt for dependencies
- Environment variables for email configuration
"""

import os
import sys
import sqlite3
import imaplib
import smtplib
import ssl
import email
import logging
import hashlib
import re
import time
import argparse
import signal
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr
from typing import Dict, List, Optional, NamedTuple
from zoneinfo import ZoneInfo
import requests
import dateparser
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from timezonefinder import TimezoneFinder

# Global scheduler variable for signal handling
scheduler = None

# Initialize timezone finder (reused across all lookups)
tf = TimezoneFinder()

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv is optional, environment variables can be set manually
    pass

# Configure logging with UTF-8 encoding to handle emojis
class SafeStreamHandler(logging.StreamHandler):
    """Custom stream handler that safely handles Unicode characters"""
    def emit(self, record):
        try:
            super().emit(record)
        except UnicodeEncodeError:
            # Fallback: encode with ascii and replace problem characters
            msg = self.format(record)
            safe_msg = msg.encode('ascii', errors='replace').decode('ascii')
            record.msg = safe_msg
            super().emit(record)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        SafeStreamHandler(sys.stderr),
        logging.FileHandler('app.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def signal_handler(signum, frame):
    """Graceful shutdown handler for Ctrl+C and other signals"""
    signal_names = {
        signal.SIGINT: "SIGINT (Ctrl+C)",
        signal.SIGTERM: "SIGTERM"
    }
    signal_name = signal_names.get(signum, f"Signal {signum}")
    
    logger.info(f"🛑 Received {signal_name} - Shutting down Daily Brief Service gracefully...")
    
    if scheduler and scheduler.running:
        logger.info("📧 Stopping email monitoring...")
        logger.info("⏰ Stopping scheduled jobs...")
        scheduler.shutdown(wait=False)
        logger.info("✅ Daily Brief Service stopped successfully")
    else:
        logger.info("⚠️ Scheduler not running, forcing exit...")
    
    print("\n👋 Daily Brief Service has been stopped. Goodbye!")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # Termination signal


class EmailMessageInfo(NamedTuple):
    """Normalized email message information."""
    uid: str
    from_email: str
    subject: str
    plain_text_body: str
    date: datetime


class Config:
    """Configuration from environment variables."""
    def __init__(self):
        self.email_address = self._get_env("EMAIL_ADDRESS")
        self.email_password = self._get_env("EMAIL_PASSWORD")
        self.imap_host = self._get_env("IMAP_HOST")
        self.imap_port = int(os.getenv("IMAP_PORT", "993"))
        self.smtp_host = self._get_env("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        self.timezone = os.getenv("TZ", "Europe/Bratislava")
        self.language = os.getenv("LANGUAGE", "en")  # Default to English
        
    def _get_env(self, key: str) -> str:
        """Get required environment variable or exit."""
        value = os.getenv(key)
        if not value:
            logger.error(f"Required environment variable {key} is not set")
            sys.exit(1)
        return value


def load_env() -> Config:
    """Load and validate environment configuration."""
    logger.info("Loading configuration from environment variables")
    config = Config()
    
    # Set timezone globally
    os.environ['TZ'] = config.timezone
    
    logger.info(f"Configuration loaded - Email: {config.email_address}, TZ: {config.timezone}")
    return config


def init_db(path: str = "app.db") -> None:
    """Initialize SQLite database with required tables."""
    logger.info(f"Initializing database at {path}")
    
    conn = sqlite3.connect(path)
    try:
        # Subscribers table for weather service
        conn.execute("""
            CREATE TABLE IF NOT EXISTS subscribers (
                email TEXT PRIMARY KEY,
                location TEXT NOT NULL,
                lat REAL NULL,
                lon REAL NULL,
                updated_at TEXT NOT NULL,
                personality TEXT DEFAULT 'neutral'
            )
        """)
        
        # Handle schema upgrades - add personality column if it doesn't exist
        try:
            conn.execute("ALTER TABLE subscribers ADD COLUMN personality TEXT DEFAULT 'neutral'")
            logger.info("Added personality column to subscribers table")
        except sqlite3.OperationalError:
            # Column already exists, which is fine
            pass
        
        # Handle schema upgrade - add language column if it doesn't exist
        try:
            conn.execute("ALTER TABLE subscribers ADD COLUMN language TEXT DEFAULT 'en'")
            logger.info("Added language column to subscribers table")
        except sqlite3.OperationalError:
            # Column already exists, which is fine
            pass
        
        # Handle schema upgrade - add timezone column if it doesn't exist
        try:
            conn.execute("ALTER TABLE subscribers ADD COLUMN timezone TEXT DEFAULT 'UTC'")
            logger.info("Added timezone column to subscribers table")
        except sqlite3.OperationalError:
            # Column already exists, which is fine
            pass
        
        # Handle schema upgrade - add last_sent_date column to track daily sends
        try:
            conn.execute("ALTER TABLE subscribers ADD COLUMN last_sent_date TEXT NULL")
            logger.info("Added last_sent_date column to subscribers table")
        except sqlite3.OperationalError:
            # Column already exists, which is fine
            pass
        
        # Reminders table for calendar service
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                message TEXT NOT NULL,
                first_run_at TEXT NOT NULL,
                remaining_repeats INTEGER NOT NULL,
                last_sent_at TEXT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        # Index for efficient reminder queries
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_reminders_email_time 
            ON reminders (email, first_run_at)
        """)
        
        # Inbox log for deduplication
        conn.execute("""
            CREATE TABLE IF NOT EXISTS inbox_log (
                uid TEXT PRIMARY KEY,
                from_email TEXT NOT NULL,
                received_at TEXT NOT NULL,
                subject TEXT,
                body_hash TEXT
            )
        """)
        
        conn.commit()
        logger.info("Database initialized successfully")
        
    finally:
        conn.close()


def imap_fetch_unseen(config: Config) -> List[EmailMessageInfo]:
    """Fetch unseen messages from IMAP inbox."""
    logger.info("Fetching unseen emails from IMAP")
    messages = []
    
    try:
        # Connect to IMAP server
        mail = imaplib.IMAP4_SSL(config.imap_host, config.imap_port)
        mail.login(config.email_address, config.email_password)
        mail.select('INBOX')
        
        # Search for unseen messages
        typ, data = mail.search(None, 'UNSEEN')
        if typ != 'OK':
            logger.warning("IMAP search failed")
            return messages
            
        message_ids = data[0].split()
        logger.info(f"Found {len(message_ids)} unseen messages")
        
        for msg_id in message_ids:
            try:
                # Fetch message
                typ, msg_data = mail.fetch(msg_id, '(RFC822)')
                if typ != 'OK':
                    continue
                    
                raw_email = msg_data[0][1]
                email_message = email.message_from_bytes(raw_email)
                
                # Extract basic info
                from_header = email_message.get('From', '')
                from_email = parseaddr(from_header)[1].lower() if from_header else ''
                subject = email_message.get('Subject', '')
                date_str = email_message.get('Date', '')
                
                # Parse date
                try:
                    msg_date = email.utils.parsedate_to_datetime(date_str)
                except:
                    msg_date = datetime.now(ZoneInfo(config.timezone))
                
                # Extract plain text body
                plain_text_body = _extract_plain_text(email_message)
                
                # Create unique UID from message ID and content hash
                uid = f"{msg_id.decode()}_{hashlib.md5(raw_email).hexdigest()[:8]}"
                
                messages.append(EmailMessageInfo(
                    uid=uid,
                    from_email=from_email,
                    subject=subject,
                    plain_text_body=plain_text_body,
                    date=msg_date
                ))
                
            except Exception as e:
                logger.error(f"Error processing message {msg_id}: {e}")
                continue
        
        mail.close()
        mail.logout()
        
    except Exception as e:
        logger.error(f"IMAP connection error: {e}")
        
    return messages


def _extract_plain_text(email_message) -> str:
    """Extract plain text from email message."""
    body = ""
    
    if email_message.is_multipart():
        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                try:
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    break
                except:
                    continue
    else:
        if email_message.get_content_type() == "text/plain":
            try:
                body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                body = ""
    
    # Clean up body - remove reply chains and signatures
    lines = body.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        
        # Stop at reply chain indicators
        if (line.startswith('On ') and ('wrote:' in line or 'sent:' in line)) or \
           line.startswith('>') or \
           line.startswith('From:') or \
           line.startswith('Sent:') or \
           line.startswith('To:') or \
           line.startswith('Subject:'):
            break
            
        # Stop at common signature patterns
        if line.startswith('--') or line.startswith('___') or \
           'sent from' in line.lower() or \
           'best regards' in line.lower() or \
           'thank you' in line.lower():
            break
            
        if line:  # Add non-empty lines
            cleaned_lines.append(line)
            
        # Limit to first 10 meaningful lines to avoid very long emails
        if len(cleaned_lines) >= 10:
            break
    
    return '\n'.join(cleaned_lines)


def mark_seen(config: Config, uid: str) -> None:
    """Mark email as seen in IMAP (not implemented for simplicity)."""
    # In a production system, you'd mark the message as seen
    # For now, we rely on deduplication via inbox_log
    pass


def send_email(config: Config, to: str, subject: str, body: str, dry_run: bool = False) -> bool:
    """Send email via SMTP."""
    if dry_run:
        logger.info(f"DRY RUN - Would send email to {to}: {subject}")
        return True
        
    logger.info(f"Sending email to {to}: {subject}")
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = config.email_address
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect and send
        if config.smtp_use_tls:
            server = smtplib.SMTP(config.smtp_host, config.smtp_port)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(config.smtp_host, config.smtp_port)
            
        server.login(config.email_address, config.email_password)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Email sent successfully to {to}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {to}: {e}")
        return False


def parse_plaintext(body: str) -> Dict:
    """
    Smart email parser - Natural language friendly!
    
    Accepts formats like:
    - "subscribe bratislava sk emuska"
    - "subscribe\nbratislava\nsk\nemuska"
    - "hello, i want weather for bratislava in slovak with emuska"
    - Old format still works: "location: Bratislava"
    
    Detects:
    - Languages: en, es, sk, english, spanish, slovak, slovenčina, español
    - Personalities: neutral, cute, brutal, emuska (+ synonyms)
    - Locations: anything else (validated by geocoding later)
    - Commands: delete, unsubscribe
    """
    body = body.strip()
    
    # Normalize text for analysis (preserve original for location extraction)
    text_lower = body.lower()
    
    # Quick check for delete command
    if 'delete' in text_lower or 'unsubscribe' in text_lower:
        return {'command': 'DELETE'}
    
    # Extract all tokens (words and phrases)
    # Split by lines and spaces, but preserve multi-word locations
    lines = [line.strip() for line in body.split('\n') if line.strip()]
    all_tokens = []
    for line in lines:
        all_tokens.extend([word.strip(',.!?;:') for word in line.split() if word.strip()])
    
    # Also keep full lines as potential locations
    full_line_tokens = [line.strip(',.!?;:') for line in lines if line.strip()]
    
    # Initialize detected values
    detected_language = None
    detected_personality = None
    detected_location = None
    
    # Language detection maps
    language_map = {
        # Language codes
        'en': 'en', 'es': 'es', 'sk': 'sk',
        # Full names
        'english': 'en', 'spanish': 'es', 'slovak': 'sk',
        # Native names
        'slovenčina': 'sk', 'slovensky': 'sk', 'slovenské': 'sk',
        'español': 'es', 'española': 'es',
    }
    
    # Personality detection maps
    personality_map = {
        # Direct keywords
        'neutral': 'neutral', 'cute': 'cute', 'brutal': 'brutal', 'emuska': 'emuska',
        # Synonyms
        'normal': 'neutral', 'standard': 'neutral', 'basic': 'neutral',
        'sweet': 'cute', 'lovely': 'cute', 'nice': 'cute', 'kind': 'cute',
        'harsh': 'brutal', 'direct': 'brutal', 'honest': 'brutal', 'straight': 'brutal',
        'princess': 'emuska', 'romantic': 'emuska', 'loving': 'emuska',
    }
    
    # Filter words to ignore (common filler words and command keywords)
    ignore_words = {
        'subscribe', 'weather', 'forecast', 'please', 'thank', 'thanks', 'hello', 
        'hi', 'hey', 'want', 'need', 'get', 'send', 'me', 'my', 'for', 'in', 
        'with', 'the', 'a', 'an', 'to', 'from', 'daily', 'service', 'i', 'id',
        'like', 'would', 'could', 'can', 'language', 'location', 'personality',
        'mode', 'type', 'style', 'prefer', 'preference', 'set', 'change',
        'update', 'modify', 'sign', 'up', 'signup', 'join', 'register',
    }
    
    # Parse tokens to detect language and personality
    location_candidates = []
    
    for i, token in enumerate(all_tokens):
        token_lower = token.lower()
        
        # Skip labels like "language:", "location:", etc.
        if token_lower.endswith(':'):
            continue
        
        # Check for language
        if token_lower in language_map and not detected_language:
            detected_language = language_map[token_lower]
            continue
        
        # Check for personality
        if token_lower in personality_map and not detected_personality:
            detected_personality = personality_map[token_lower]
            continue
        
        # If it's not a filler word and not already detected as lang/personality
        if token_lower not in ignore_words and len(token) > 1:
            location_candidates.append(token)
    
    # Also check full lines for location (better for "Bratislava, Slovakia" style)
    for line in full_line_tokens:
        line_lower = line.lower()
        
        # Skip if it's a language or personality keyword
        is_keyword = False
        for keyword in list(language_map.keys()) + list(personality_map.keys()):
            if line_lower == keyword:
                is_keyword = True
                break
        
        if not is_keyword and len(line) > 2:
            # Remove label prefixes
            line_clean = re.sub(r'^(location|city|place|where):\s*', '', line, flags=re.IGNORECASE)
            if line_clean and line_clean.lower() not in ignore_words:
                location_candidates.append(line_clean)
    
    # Smart location selection: prefer longer, more specific strings
    if location_candidates:
        # Sort by length (longer = more specific like "Bratislava, Slovakia" vs "Bratislava")
        location_candidates = sorted(set(location_candidates), key=len, reverse=True)
        
        # Filter out candidates that are substrings of longer candidates
        final_location = None
        for candidate in location_candidates:
            # Check if this candidate contains any language/personality keywords
            candidate_lower = candidate.lower()
            has_keyword = False
            for keyword in list(language_map.keys()) + list(personality_map.keys()):
                if keyword in candidate_lower.split():
                    has_keyword = True
                    break
            
            if not has_keyword:
                final_location = candidate
                break
        
        detected_location = final_location or location_candidates[0]
    
    # Determine command type
    # If only personality is detected, it's a personality change
    if detected_personality and not detected_location:
        return {'command': 'PERSONALITY', 'mode': detected_personality}
    
    # If only language is detected, it's a language change
    if detected_language and not detected_location and not detected_personality:
        return {'command': 'LANGUAGE', 'language': detected_language}
    
    # Otherwise, it's a weather subscription/update
    if detected_location:
        result = {
            'command': 'WEATHER',
            'location': detected_location
        }
        
        # Add optional parameters if detected
        if detected_personality:
            result['personality'] = detected_personality
        if detected_language:
            result['language'] = detected_language
        
        return result
    
    # Fallback - no clear command detected
    # Try to use first non-keyword line as location
    for line in full_line_tokens:
        if len(line) > 2 and line.lower() not in ignore_words:
            return {'command': 'WEATHER', 'location': line}
    
    # Ultimate fallback
    return {'command': 'WEATHER', 'location': full_line_tokens[0] if full_line_tokens else 'current'}


def load_weather_messages(file_path: str = None, language: str = "en") -> Dict[str, Dict[str, str]]:
    """Load weather messages from configuration file."""
    if file_path is None:
        file_path = f"languages/{language}/weather_messages.txt"
        # Fallback to root directory for backward compatibility
        if not os.path.exists(file_path):
            file_path = "weather_messages.txt"
    
    messages = {}
    
    try:
        if not os.path.exists(file_path):
            logger.warning(f"Weather messages file {file_path} not found, using defaults")
            return _get_default_weather_messages()
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse format: condition|neutral|cute|brutal|emuska
                parts = line.split('|')
                if len(parts) != 5:
                    logger.warning(f"Invalid format in {file_path} line {line_num}: {line}")
                    continue
                
                condition, neutral, cute, brutal, emuska = parts
                messages[condition.strip()] = {
                    'neutral': neutral.strip(),
                    'cute': cute.strip(), 
                    'brutal': brutal.strip(),
                    'emuska': emuska.strip()
                }
        
        logger.info(f"Loaded {len(messages)} weather message conditions")
        return messages
        
    except Exception as e:
        logger.error(f"Error loading weather messages from {file_path}: {e}")
        return _get_default_weather_messages()


def _get_default_weather_messages() -> Dict[str, Dict[str, str]]:
    """Return default weather messages if file loading fails."""
    return {
        'default': {
            'neutral': 'Check current conditions and dress accordingly.',
            'cute': '🌤️ Whatever the weather brings, you\'ve got this! Have a wonderful day! 💖',
            'brutal': 'Weather is weather. Dress like a functional human being.',
            'emuska': ''
        },
        'raining': {
            'neutral': 'Take an umbrella - it\'s going to rain today.',
            'cute': '🌧️ Pitter-patter raindrops are coming! Don\'t forget your cute umbrella! ☂️',
            'brutal': 'Rain incoming. Umbrella or get soaked. Your choice.',
            'emuska': ''
        },
        'sunny': {
            'neutral': 'Beautiful sunny day - perfect weather to enjoy outdoors.',
            'cute': '☀️ Glorious sunshine day! Time for outdoor adventures and happy vibes! 🌻',
            'brutal': 'Clear skies. No excuses to stay inside feeling sorry for yourself.',
            'emuska': ''
        }
    }


def detect_weather_condition(weather: Dict) -> str:
    """Analyze weather data and return the primary condition."""
    temp_max = weather['temp_max']
    temp_min = weather['temp_min']
    precip_prob = weather['precipitation_probability']
    precip_sum = weather['precipitation_sum']
    wind_speed = weather['wind_speed_max']
    
    # Temperature-based conditions (check extremes first)
    if temp_max >= 35:
        return 'heatwave' if temp_max >= 40 else 'sunny_hot'
    elif temp_max <= -10:
        return 'blizzard' if precip_sum > 10 and wind_speed > 50 else 'freezing'
    elif temp_max <= 0:
        if precip_sum > 5:
            return 'snowing'
        else:
            return 'freezing'
    elif temp_max <= 5:
        if wind_speed > 30:
            return 'cold_windy'
        elif precip_sum > 2:
            return 'rainy_cold'
        else:
            return 'cold'
    elif temp_max >= 30:
        return 'hot'
    
    # Precipitation conditions
    if precip_sum > 20 or precip_prob > 80:
        if wind_speed > 40:
            return 'thunderstorm'
        elif precip_sum > 50:
            return 'heavy_rain'
        elif temp_max <= 10:
            return 'rainy_cold'
        else:
            return 'raining'
    elif precip_sum > 0 or precip_prob > 50:
        return 'raining'
    
    # Wind conditions
    if wind_speed > 60:
        return 'stormy'
    elif wind_speed > 40:
        return 'thunderstorm' if precip_prob > 30 else 'windy'
    elif wind_speed > 25:
        return 'windy'
    
    # Clear/mild conditions
    if precip_prob < 20 and wind_speed < 20:
        if temp_max >= 20 and temp_max <= 28:
            return 'mild'
        elif precip_prob < 10:
            return 'sunny'
        else:
            return 'cloudy'
    
    # Default fallback
    return 'default'


def get_weather_message(condition: str, personality: str = 'neutral', messages: Dict = None, language: str = 'en') -> str:
    """Get weather message for specific condition and personality mode."""
    if messages is None:
        messages = load_weather_messages(language=language)
    
    # Normalize personality mode
    personality = personality.lower().strip()
    if personality not in ['neutral', 'cute', 'brutal', 'emuska']:
        personality = 'neutral'
    
    # Special handling for Emuska mode - only available in Slovak
    if personality == 'emuska' and language != 'sk':
        logger.warning(f"Emuska mode requested for {language} language, falling back to 'cute'")
        personality = 'cute'  # Fallback to cute mode for non-Slovak languages
    
    # Get message for condition
    if condition in messages:
        # Check if the personality exists and has content for this language
        message = messages[condition].get(personality, '')
        if not message and personality == 'emuska':
            # If Emuska message is empty, fallback to cute
            message = messages[condition].get('cute', messages.get('default', {}).get('cute', 'Have a great day!'))
        return message or messages.get('default', {}).get(personality, 'Have a great day!')
    else:
        # Fallback to default
        return messages.get('default', {}).get(personality, 'Have a great day!')


def geocode_location(location: str) -> Optional[tuple]:
    """Geocode location using Open-Meteo Geocoding API and determine timezone."""
    logger.info(f"Geocoding location: {location}")
    
    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {
            'name': location,
            'count': 1,
            'language': 'en',
            'format': 'json'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('results'):
            result = data['results'][0]
            lat = result['latitude']
            lon = result['longitude']
            name = result['name']
            country = result.get('country', '')
            admin1 = result.get('admin1', '')
            
            display_name = f"{name}"
            if admin1:
                display_name += f", {admin1}"
            if country:
                display_name += f", {country}"
            
            # Determine timezone from coordinates
            timezone = tf.timezone_at(lat=lat, lng=lon)
            if not timezone:
                logger.warning(f"Could not determine timezone for {lat}, {lon}, defaulting to UTC")
                timezone = "UTC"
            
            logger.info(f"Geocoded '{location}' to {lat}, {lon} ({display_name}) - Timezone: {timezone}")
            return lat, lon, display_name, timezone
        else:
            logger.warning(f"No geocoding results for: {location}")
            return None
            
    except Exception as e:
        logger.error(f"Geocoding error for '{location}': {e}")
        return None


def get_weather_forecast(lat: float, lon: float, timezone_name: str) -> Optional[Dict]:
    """Get weather forecast from Open-Meteo API."""
    logger.info(f"Getting weather forecast for {lat}, {lon}")
    
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': lat,
            'longitude': lon,
            'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,precipitation_probability_max',
            'timezone': timezone_name,
            'forecast_days': 1
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('daily'):
            daily = data['daily']
            return {
                'temp_max': daily['temperature_2m_max'][0],
                'temp_min': daily['temperature_2m_min'][0],
                'precipitation_sum': daily['precipitation_sum'][0],
                'precipitation_probability': daily['precipitation_probability_max'][0],
                'wind_speed_max': daily['wind_speed_10m_max'][0]
            }
        else:
            logger.warning(f"No weather data returned for {lat}, {lon}")
            return None
            
    except Exception as e:
        logger.error(f"Weather API error for {lat}, {lon}: {e}")
        return None


def generate_weather_summary(weather: Dict, location: str, personality: str = 'neutral', language: str = 'en') -> str:
    """Generate natural language weather summary with clothing recommendation and personality."""
    temp_max = weather['temp_max']
    temp_min = weather['temp_min']
    precip_prob = weather['precipitation_probability']
    precip_sum = weather['precipitation_sum']
    wind_speed = weather['wind_speed_max']
    
    # Load weather messages for the specified language
    messages = load_weather_messages(language=language)
    
    # Detect primary weather condition
    condition = detect_weather_condition(weather)
    
    # Generate summary
    summary = f"Today's weather for {location}:\n\n"
    summary += f"🌡️ Temperature: High {temp_max:.0f}°C / Low {temp_min:.0f}°C\n"
    summary += f"🌧️ Rain probability: {precip_prob:.0f}%"
    
    if precip_sum > 0:
        summary += f" (≈{precip_sum:.1f} mm)"
    summary += "\n"
    
    summary += f"💨 Wind: up to {wind_speed:.0f} km/h\n\n"
    
    # Get personality-based weather message
    weather_message = get_weather_message(condition, personality, messages, language)
    summary += f"💡 {weather_message}\n\n"
    
    # Generate clothing recommendation based on personality and language
    clothing = _generate_clothing_advice(temp_max, precip_prob, precip_sum, wind_speed, personality, language)
    summary += clothing + "\n"
    
    return summary


def _generate_clothing_advice(temp_max: float, precip_prob: float, precip_sum: float, wind_speed: float, personality: str, language: str = 'en') -> str:
    """Generate clothing advice based on weather conditions and personality mode."""
    
    # Localized clothing items
    clothing_texts = {
        'en': {
            'very_cold': "heavy winter coat, thermal layers, warm boots",
            'cold': "heavy winter coat, warm layers, gloves",
            'cool': "warm jacket and layers",
            'mild': "light jacket or sweater",
            'warm': "light clothing, t-shirt",
            'rain_heavy': "rain jacket, waterproof shoes",
            'rain_light': "umbrella handy",
            'wind': "windproof outer layer"
        },
        'es': {
            'very_cold': "abrigo de invierno pesado, capas térmicas, botas cálidas",
            'cold': "abrigo de invierno pesado, capas cálidas, guantes",
            'cool': "chaqueta abrigada y capas",
            'mild': "chaqueta ligera o suéter",
            'warm': "ropa ligera, camiseta",
            'rain_heavy': "chaqueta impermeable, zapatos impermeables",
            'rain_light': "paraguas a mano",
            'wind': "capa exterior cortavientos"
        },
        'sk': {
            'very_cold': "ťažký zimný kabát, termo vrstvy, teplé topánky",
            'cold': "ťažký zimný kabát, teplé vrstvy, rukavice",
            'cool': "teplá bunda a viac vrstiev",
            'mild': "ľahká bunda alebo sveter",
            'warm': "ľahké oblečenie, tričko",
            'rain_heavy': "nepremokavá bunda, vodotesné topánky",
            'rain_light': "dáždnik poruke",
            'wind': "vetrovka alebo vetruodolná vrstva"
        }
    }
    
    texts = clothing_texts.get(language, clothing_texts['en'])
    base_clothing = []
    accessories = []
    
    # Temperature-based clothing
    if temp_max < 0:
        base_clothing.append(texts['very_cold'])
    elif temp_max < 5:
        base_clothing.append(texts['cold'])
    elif temp_max < 15:
        base_clothing.append(texts['cool'])
    elif temp_max < 25:
        base_clothing.append(texts['mild'])
    else:
        base_clothing.append(texts['warm'])
    
    # Precipitation accessories
    if precip_prob > 50 or precip_sum > 1:
        accessories.append(texts['rain_heavy'])
    elif precip_prob > 20:
        accessories.append(texts['rain_light'])
    
    # Wind protection
    if wind_speed > 30:
        accessories.append(texts['wind'])
    
    # Combine advice
    clothing_items = base_clothing + accessories
    clothing_text = ", ".join(clothing_items)
    
    # Add personality-based prefix (localized)
    prefixes = {
        'en': {
            'cute': ("👕 Fashion advice: Wear ", " and look absolutely adorable! 💖"),
            'brutal': ("🥶 Survival gear: ", " or suffer the consequences."),
            'emuska': ("👗 Pre moju princeznú: Oblieč si ", ", aby si bola krásna a chránená ako skutočná kráľovná! 💕👸✨"),
            'neutral': ("👕 Clothing recommendation: ", "")
        },
        'es': {
            'cute': ("👕 Consejo de moda: Usa ", " ¡y luce absolutamente adorable! 💖"),
            'brutal': ("🥶 Equipo de supervivencia: ", " o sufre las consecuencias."),
            'emuska': ("👗 Pre moju princeznú: Oblieč si ", ", aby si bola krásna a chránená ako skutočná kráľovná! 💕👸✨"),
            'neutral': ("👕 Recomendación de ropa: ", "")
        },
        'sk': {
            'cute': ("👕 Módna rada: Obleč si ", " a vyzeraj úplne roztomilo! 💖"),
            'brutal': ("🥶 Výbava na prežitie: ", " alebo trp následky."),
            'emuska': ("👗 Pre moju princeznú: Oblieč si ", ", aby si bola krásna a chránená ako skutočná kráľovná! 💕👸✨"),
            'neutral': ("👕 Odporúčanie oblečenia: ", "")
        }
    }
    
    lang_prefixes = prefixes.get(language, prefixes['en'])
    prefix, suffix = lang_prefixes.get(personality, lang_prefixes['neutral'])
    
    return prefix + clothing_text + suffix


def handle_weather_command(config: Config, from_email: str, location: str = None, is_delete: bool = False, personality: str = None, language: str = None, dry_run: bool = False) -> None:
    """Handle weather subscription command."""
    conn = sqlite3.connect("app.db")
    
    try:
        if is_delete:
            # Remove subscriber
            cursor = conn.execute("DELETE FROM subscribers WHERE email = ?", (from_email,))
            if cursor.rowcount > 0:
                conn.commit()
                response = f"✅ You've been unsubscribed from the daily weather service.\n\n"
            else:
                response = f"ℹ️ You weren't subscribed to the weather service.\n\n"
        else:
            # Get current subscriber info
            current_sub = conn.execute("""
                SELECT location, lat, lon, personality, COALESCE(language, 'en') FROM subscribers WHERE email = ?
            """, (from_email,)).fetchone()
            
            current_location = current_sub[0] if current_sub else None
            current_lat = current_sub[1] if current_sub else None  
            current_lon = current_sub[2] if current_sub else None
            current_personality = current_sub[3] if current_sub else 'neutral'
            current_language = current_sub[4] if current_sub else 'en'
            
            # Determine what to update
            new_location = location if location else current_location
            new_personality = personality if personality else current_personality
            new_language = language if language else current_language
            
            # Validate Emuska personality mode - only available in Slovak
            if new_personality == 'emuska' and new_language != 'sk':
                response = f"❌ Emuska personality mode is only available in Slovak language.\n"
                response += f"Please set language to 'sk' to use Emuska mode, or choose another personality: neutral, cute, brutal\n\n"
                response += _get_usage_footer()
                send_email(config, from_email, "Weather Service - Language Error", response, dry_run)
                return
            
            if new_location:
                # Subscribe/update location
                geocode_result = geocode_location(new_location) if new_location != current_location else None
                
                if geocode_result and geocode_result[0] is not None:
                    lat, lon, display_name, timezone_str = geocode_result
                    
                    # Save/update subscription with timezone
                    conn.execute("""
                        INSERT OR REPLACE INTO subscribers (email, location, lat, lon, timezone, updated_at, personality, language)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (from_email, display_name, lat, lon, timezone_str, datetime.now(ZoneInfo(config.timezone)).isoformat(), new_personality, new_language))
                    conn.commit()
                    
                    # Get sample weather with personality and language (use subscriber's timezone)
                    weather = get_weather_forecast(lat, lon, timezone_str)
                    if weather:
                        sample_forecast = generate_weather_summary(weather, display_name, new_personality, new_language)
                        response = f"✅ Weather subscription updated!\n"
                        response += f"📍 Location: {display_name} ({lat:.4f}, {lon:.4f})\n"
                        response += f"🌍 Timezone: {timezone_str}\n"
                        response += f"🎭 Personality mode: {new_personality}\n"
                        response += f"🌍 Language: {new_language}\n"
                        response += f"⏰ Daily forecast will be sent at 05:00 {timezone_str} time\n\n"
                        response += f"Here's today's forecast:\n{sample_forecast}\n"
                    else:
                        response = f"✅ Subscribed to weather for {display_name} in {new_personality} mode, but couldn't fetch current forecast.\n\n"
                elif current_lat and current_lon:
                    # Just update personality/language, keep existing location and coordinates
                    conn.execute("""
                        UPDATE subscribers 
                        SET personality = ?, language = ?, updated_at = ?
                        WHERE email = ?
                    """, (new_personality, new_language, datetime.now(ZoneInfo(config.timezone)).isoformat(), from_email))
                    conn.commit()
                    
                    response = f"✅ Updated to {new_personality} mode (language: {new_language})\n"
                    response += f"Location unchanged: {current_location}\n\n"
                else:
                    # Save with unknown coordinates
                    conn.execute("""
                        INSERT OR REPLACE INTO subscribers (email, location, lat, lon, timezone, updated_at, personality, language)
                        VALUES (?, ?, NULL, NULL, 'UTC', ?, ?, ?)
                    """, (from_email, new_location, datetime.now(ZoneInfo(config.timezone)).isoformat(), new_personality, new_language))
                    conn.commit()
                    
                    response = f"⚠️ Subscribed to weather service in {new_personality} mode (language: {new_language}), but couldn't geocode '{new_location}'.\n"
                    response += "Please try a more specific location (e.g., 'Prague, CZ' or 'New York, NY').\n\n"
            else:
                response = f"❌ Please provide a location to subscribe to weather updates.\n\n"
        
        # Add usage instructions
        response += _get_usage_footer()
        
        # Send reply
        subject = "Weather Service - Subscription Update"
        send_email(config, from_email, subject, response, dry_run)
        
    finally:
        conn.close()


def handle_personality_command(config: Config, from_email: str, mode: str, dry_run: bool = False) -> None:
    """Handle personality mode change command."""
    conn = sqlite3.connect("app.db")
    
    try:
        # Validate personality mode
        if mode not in ['neutral', 'cute', 'brutal', 'emuska']:
            response = f"❌ Invalid personality mode '{mode}'. Choose from: neutral, cute, brutal, emuska\n\n"
            response += _get_usage_footer()
            send_email(config, from_email, "Personality Mode - Error", response, dry_run)
            return
        
        # Check if user is subscribed to weather service and get their language
        current_sub = conn.execute("""
            SELECT location, lat, lon, COALESCE(language, 'en') FROM subscribers WHERE email = ?
        """, (from_email,)).fetchone()
        
        if current_sub:
            location, lat, lon, user_language = current_sub
            
            # Validate Emuska personality mode - only available in Slovak
            if mode == 'emuska' and user_language != 'sk':
                response = f"❌ Emuska personality mode is only available in Slovak language.\n"
                response += f"Your current language: {user_language}\n"
                response += f"Please change language to 'sk' first, or choose another personality: neutral, cute, brutal\n\n"
                response += _get_usage_footer()
                send_email(config, from_email, "Personality Mode - Language Error", response, dry_run)
                return
            
            # Update existing subscription personality
            conn.execute("""
                UPDATE subscribers SET personality = ?, updated_at = ? WHERE email = ?
            """, (mode, datetime.now(ZoneInfo(config.timezone)).isoformat(), from_email))
            conn.commit()
            
            # Show sample with new personality
            if lat and lon:
                weather = get_weather_forecast(lat, lon, config.timezone)
                if weather:
                    sample_forecast = generate_weather_summary(weather, location, mode, user_language)
                    response = f"✅ Personality mode updated to '{mode}'!\n\n"
                    response += f"Here's how your weather reports will look:\n{sample_forecast}\n"
                else:
                    response = f"✅ Personality mode updated to '{mode}' for {location}!\n\n"
            else:
                response = f"✅ Personality mode updated to '{mode}' for {location}!\n\n"
        else:
            response = f"ℹ️ You're not subscribed to the weather service yet.\n"
            response += f"Send a location to subscribe with '{mode}' personality mode.\n\n"
        
        response += _get_usage_footer()
        send_email(config, from_email, f"Personality Mode - {mode.title()}", response, dry_run)
        
    finally:
        conn.close()


def handle_language_command(config: Config, from_email: str, language: str, dry_run: bool = False) -> None:
    """Handle language change command."""
    conn = sqlite3.connect("app.db")
    
    try:
        # Validate language code
        if language not in ['en', 'es', 'sk']:
            response = f"❌ Invalid language '{language}'. Choose from: en (English), es (Spanish), sk (Slovak)\n\n"
            response += _get_usage_footer()
            send_email(config, from_email, "Language - Error", response, dry_run)
            return
        
        # Check if user is subscribed to weather service
        current_sub = conn.execute("""
            SELECT location, lat, lon, COALESCE(personality, 'neutral') FROM subscribers WHERE email = ?
        """, (from_email,)).fetchone()
        
        if current_sub:
            location, lat, lon, personality = current_sub
            
            # Update existing subscription language
            conn.execute("""
                UPDATE subscribers SET language = ?, updated_at = ? WHERE email = ?
            """, (language, datetime.now(ZoneInfo(config.timezone)).isoformat(), from_email))
            conn.commit()
            
            # Show sample with new language
            if lat and lon:
                weather = get_weather_forecast(lat, lon, config.timezone)
                if weather:
                    sample_forecast = generate_weather_summary(weather, location, personality, language)
                    response = f"✅ Language updated to '{language}'!\n\n"
                    response += f"Here's how your weather reports will look:\n{sample_forecast}\n"
                else:
                    response = f"✅ Language updated to '{language}' for {location}!\n\n"
            else:
                response = f"✅ Language updated to '{language}' for {location}!\n\n"
        else:
            response = f"ℹ️ You're not subscribed to the weather service yet.\n"
            response += f"Send a location to subscribe with '{language}' language.\n\n"
        
        response += _get_usage_footer()
        send_email(config, from_email, f"Language - {language.upper()}", response, dry_run)
        
    finally:
        conn.close()


def handle_calendar_command(config: Config, from_email: str, fields: Dict, dry_run: bool = False) -> None:
    """Handle calendar reminder command."""
    conn = sqlite3.connect("app.db")
    
    try:
        # Validate required fields
        if 'message' not in fields:
            response = "❌ Error: 'message' field is required for calendar reminders.\n\n"
            response += _get_usage_footer()
            send_email(config, from_email, "Calendar Reminder - Error", response, dry_run)
            return
        
        # Parse date and time
        date_str = fields.get('date', 'today')
        time_str = fields.get('time', '09:00')
        repeat_count = int(fields.get('repeat', '1'))
        
        # Combine date and time for parsing
        datetime_str = f"{date_str} {time_str}"
        
        # Parse with timezone
        parsed_dt = dateparser.parse(
            datetime_str,
            settings={
                'TIMEZONE': config.timezone,
                'RETURN_AS_TIMEZONE_AWARE': True,
                'TO_TIMEZONE': config.timezone
            }
        )
        
        if not parsed_dt:
            response = f"❌ Error: Couldn't parse date/time '{datetime_str}'.\n"
            response += "Try formats like: 'tomorrow 2pm', '2025-12-01 08:30', 'next Friday 9am'\n\n"
            response += _get_usage_footer()
            send_email(config, from_email, "Calendar Reminder - Error", response, dry_run)
            return
        
        # Ensure we're scheduling for the future
        now = datetime.now(ZoneInfo(config.timezone))
        if parsed_dt <= now:
            response = f"❌ Error: Cannot schedule reminder in the past.\n"
            response += f"Parsed time: {parsed_dt.strftime('%Y-%m-%d %H:%M %Z')}\n"
            response += f"Current time: {now.strftime('%Y-%m-%d %H:%M %Z')}\n\n"
            response += _get_usage_footer()
            send_email(config, from_email, "Calendar Reminder - Error", response, dry_run)
            return
        
        # Save reminder
        remaining_repeats = max(0, repeat_count - 1)  # First send doesn't count as repeat
        
        conn.execute("""
            INSERT INTO reminders (email, message, first_run_at, remaining_repeats, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            from_email,
            fields['message'],
            parsed_dt.isoformat(),
            remaining_repeats,
            now.isoformat()
        ))
        conn.commit()
        
        # Generate schedule summary
        response = f"✅ Calendar reminder scheduled!\n\n"
        response += f"📝 Message: {fields['message']}\n"
        response += f"📅 First reminder: {parsed_dt.strftime('%Y-%m-%d %H:%M %Z')}\n"
        
        if repeat_count > 1:
            response += f"🔄 Total reminders: {repeat_count} (every 10 minutes)\n"
            last_reminder = parsed_dt + timedelta(minutes=10 * remaining_repeats)
            response += f"📅 Last reminder: {last_reminder.strftime('%Y-%m-%d %H:%M %Z')}\n"
        
        response += f"\n💡 To delete all your pending reminders, just reply with 'delete'.\n\n"
        response += _get_usage_footer()
        
        send_email(config, from_email, "Calendar Reminder - Scheduled", response, dry_run)
        
    except ValueError as e:
        response = f"❌ Error: Invalid repeat count. Must be a positive number.\n\n"
        response += _get_usage_footer()
        send_email(config, from_email, "Calendar Reminder - Error", response, dry_run)
    except Exception as e:
        logger.error(f"Calendar command error: {e}")
        response = f"❌ Error processing calendar reminder: {str(e)}\n\n"
        response += _get_usage_footer()
        send_email(config, from_email, "Calendar Reminder - Error", response, dry_run)
    finally:
        conn.close()


def delete_all_reminders(config: Config, from_email: str, dry_run: bool = False) -> None:
    """Delete all pending reminders for a user."""
    conn = sqlite3.connect("app.db")
    
    try:
        cursor = conn.execute("DELETE FROM reminders WHERE email = ?", (from_email,))
        deleted_count = cursor.rowcount
        conn.commit()
        
        if deleted_count > 0:
            response = f"✅ Deleted {deleted_count} pending reminder(s).\n\n"
        else:
            response = f"ℹ️ No pending reminders found to delete.\n\n"
        
        response += _get_usage_footer()
        send_email(config, from_email, "Calendar Reminders - Deleted", response, dry_run)
        
    finally:
        conn.close()


def _get_usage_footer() -> str:
    """Get usage instructions footer."""
    return """📖 USAGE GUIDE:

🌤️ WEATHER SERVICE:
• Just send your location: "Bratislava", "Madrid, Spain", "New York"
• Add language: "Bratislava sk" or "Madrid español"
• Add personality: "Bratislava sk emuska" or "Madrid cute"
• Send "delete" to unsubscribe from daily weather
• Daily forecast sent at 05:00 local time

🎭 PERSONALITY MODES:
• neutral - Standard weather reports
• cute - Friendly, emoji-friendly reports 
• brutal - Blunt, no-nonsense reports
• emuska - Romantic Slovak-style reports (SK only)

🌍 LANGUAGES:
• en / english - English reports
• es / español - Spanish reports  
• sk / slovenčina - Slovak reports

💡 EXAMPLES:
• "Bratislava" → subscribes with default settings
• "Madrid es cute" → Spanish language, cute personality
• "New York brutal" → English, brutal personality
• "Prague sk emuska" → Slovak, emuska personality

Need help? Just reply to this email!"""


def run_daily_weather_job(config: Config, dry_run: bool = False) -> None:
    """Send daily weather forecast to all subscribers at 5 AM Bratislava time."""
    logger.info("Running daily weather job - sending to all subscribers")
    
    conn = sqlite3.connect("app.db")
    try:
        # Get all subscribers with timezone info
        subscribers = conn.execute("""
            SELECT email, location, lat, lon, COALESCE(timezone, 'Europe/Bratislava') as timezone,
                   COALESCE(personality, 'neutral') as personality, 
                   COALESCE(language, 'en') as language,
                   last_sent_date
            FROM subscribers 
            WHERE lat IS NOT NULL AND lon IS NOT NULL
        """).fetchall()
        
        logger.info(f"Sending daily weather to {len(subscribers)} subscribers")
        sent_count = 0
        
        # Get today's date in Bratislava timezone
        bratislava_now = datetime.now(ZoneInfo('Europe/Bratislava'))
        today_date = bratislava_now.date().isoformat()
        
        for email_addr, location, lat, lon, subscriber_tz, personality, language, last_sent_date in subscribers:
            try:
                # Check if we haven't sent today (prevent double-sending if job runs twice)
                if last_sent_date == today_date:
                    logger.info(f"Already sent to {email_addr} today, skipping")
                    continue
                    
                logger.info(f"Sending to {email_addr} at {location} (timezone: {subscriber_tz})")
                
                # Get weather forecast using subscriber's timezone
                weather = get_weather_forecast(lat, lon, subscriber_tz)
                if not weather:
                    logger.warning(f"No weather data for {email_addr} at {location}")
                    continue
                
                # Generate and send forecast with personality and language
                summary = generate_weather_summary(weather, location, personality, language)
                subject = f"Today's Weather for {location}"
                
                footer = f"\n\n---\nDaily Weather Service ({personality} mode, {language})\nTo unsubscribe, reply with 'delete'"
                full_message = summary + footer
                
                if send_email(config, email_addr, subject, full_message, dry_run):
                    # Update last_sent_date to prevent double-sending
                    conn.execute("""
                        UPDATE subscribers 
                        SET last_sent_date = ?
                        WHERE email = ?
                    """, (today_date, email_addr))
                    conn.commit()
                    sent_count += 1
                    logger.info(f"✅ Sent weather to {email_addr} ({sent_count} total)")
                else:
                    logger.warning(f"Failed to send email to {email_addr}")
                
            except Exception as e:
                logger.error(f"Error processing subscriber {email_addr}: {e}")
        
        if sent_count > 0:
            logger.info(f"✅ Daily weather job complete - sent {sent_count} emails")
        else:
            logger.info("No emails sent - check subscriber list or configuration")
                
    finally:
        conn.close()


def run_due_reminders_job(config: Config, dry_run: bool = False) -> None:
    """Send due calendar reminders."""
    now = datetime.now(ZoneInfo(config.timezone))
    conn = sqlite3.connect("app.db")
    
    try:
        # Find due reminders
        reminders = conn.execute("""
            SELECT id, email, message, first_run_at, remaining_repeats, last_sent_at
            FROM reminders
            WHERE (last_sent_at IS NULL AND ? >= first_run_at)
               OR (last_sent_at IS NOT NULL AND remaining_repeats > 0 
                   AND ? >= datetime(last_sent_at, '+10 minutes'))
            ORDER BY first_run_at
        """, (now.isoformat(), now.isoformat())).fetchall()
        
        if reminders:
            logger.info(f"Processing {len(reminders)} due reminders")
        
        for reminder_id, email_addr, message, first_run_at, remaining_repeats, last_sent_at in reminders:
            try:
                # Send reminder
                subject = "📅 Calendar Reminder"
                body = f"🔔 Reminder: {message}\n\n"
                body += f"Scheduled for: {first_run_at}\n"
                
                if remaining_repeats > 0:
                    body += f"Remaining repeats: {remaining_repeats}\n"
                
                body += "\n---\nCalendar Reminder Service\nTo delete all reminders, reply with 'delete'"
                
                if send_email(config, email_addr, subject, body, dry_run):
                    # Update reminder status
                    new_remaining = remaining_repeats - 1 if last_sent_at else remaining_repeats
                    
                    if new_remaining >= 0:
                        conn.execute("""
                            UPDATE reminders 
                            SET last_sent_at = ?, remaining_repeats = ?
                            WHERE id = ?
                        """, (now.isoformat(), new_remaining, reminder_id))
                    
                    # Clean up completed reminders
                    if new_remaining <= 0:
                        conn.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
                    
                    conn.commit()
                    logger.info(f"Sent reminder {reminder_id} to {email_addr}")
                    
            except Exception as e:
                logger.error(f"Error sending reminder {reminder_id}: {e}")
                
    finally:
        conn.close()


def process_inbound_email(config: Config, msg: EmailMessageInfo, dry_run: bool = False) -> None:
    """Process an inbound email command."""
    logger.info(f"Received email from {msg.from_email}: {msg.subject}")
    
    # Filter out system emails and unwanted messages
    if not should_process_email(msg):
        return
    
    logger.info(f"Processing valid user email from {msg.from_email}: {msg.subject}")
    
    # Check for duplicates
    conn = sqlite3.connect("app.db")
    try:
        existing = conn.execute("SELECT 1 FROM inbox_log WHERE uid = ?", (msg.uid,)).fetchone()
        if existing:
            logger.info(f"Skipping duplicate message {msg.uid}")
            return
        
        # Log message
        body_hash = hashlib.md5(msg.plain_text_body.encode()).hexdigest()
        conn.execute("""
            INSERT INTO inbox_log (uid, from_email, received_at, subject, body_hash)
            VALUES (?, ?, ?, ?, ?)
        """, (msg.uid, msg.from_email, msg.date.isoformat(), msg.subject, body_hash))
        conn.commit()
        
    finally:
        conn.close()
    
    # Parse command
    try:
        parsed = parse_plaintext(msg.plain_text_body)
        command = parsed.get('command')
        
        if command == 'DELETE':
            # Delete weather subscription (reminder system disabled)
            handle_weather_command(config, msg.from_email, is_delete=True, dry_run=dry_run)
            # delete_all_reminders(config, msg.from_email, dry_run=dry_run)  # Reminder system disabled
            
            # Send confirmation
            response = "✅ Unsubscribed from weather service\n\n"
            response += _get_usage_footer()
            send_email(config, msg.from_email, "Weather Service - Unsubscribed", response, dry_run)
            
        elif command == 'WEATHER':
            personality = parsed.get('personality', None)
            language = parsed.get('language', None)
            handle_weather_command(config, msg.from_email, parsed['location'], personality=personality, language=language, dry_run=dry_run)
            
        elif command == 'PERSONALITY':
            handle_personality_command(config, msg.from_email, parsed['mode'], dry_run=dry_run)
            
        elif command == 'LANGUAGE':
            handle_language_command(config, msg.from_email, parsed['language'], dry_run=dry_run)
            
        # elif command == 'CALENDAR':
        #     handle_calendar_command(config, msg.from_email, parsed, dry_run=dry_run)
        #     # Calendar system temporarily disabled
            
        else:
            # Unknown command
            response = "❓ I couldn't understand your request.\n\n"
            response += _get_usage_footer()
            send_email(config, msg.from_email, "Daily Brief Service - Help", response, dry_run)
            
    except Exception as e:
        logger.error(f"Error processing email from {msg.from_email}: {e}")
        response = f"❌ Error processing your request: {str(e)}\n\n"
        response += _get_usage_footer()
        send_email(config, msg.from_email, "Daily Brief Service - Error", response, dry_run)


def should_process_email(msg: EmailMessageInfo) -> bool:
    """Determine if an email should be processed by our service."""
    
    # Skip emails from system/automated accounts
    system_senders = [
        'no-reply@google.com',
        'no-reply@accounts.google.com',
        'noreply@google.com',
        'mailer-daemon@googlemail.com',
        'mailer-daemon@gmail.com',
        'bounce@',
        'postmaster@',
        'daemon@',
        'system@'
    ]
    
    # Check if sender is a system account
    sender = msg.from_email.lower()
    for system_sender in system_senders:
        if sender.startswith(system_sender.lower()):
            logger.info(f"Skipping system email from {msg.from_email}")
            return False
    
    # Skip emails with encoded subjects (usually system emails)
    if '=?' in msg.subject and '?=' in msg.subject:
        logger.info(f"Skipping email with encoded subject: {msg.subject}")
        return False
    
    # Skip emails with system-like subjects
    system_subjects = [
        'delivery status notification',
        'security alert',
        'account notification',
        'two-factor authentication',
        'your account',
        'security code',
        'verify',
        'confirmation'
    ]
    
    subject_lower = msg.subject.lower()
    for system_subject in system_subjects:
        if system_subject in subject_lower:
            logger.info(f"Skipping system email with subject: {msg.subject}")
            return False
    
    # Skip emails with very short or empty body (likely system emails)
    body_text = msg.plain_text_body.strip()
    if len(body_text) < 3:
        logger.info(f"Skipping email with too short body from {msg.from_email}")
        return False
    
    # Skip emails that look like automated responses
    if any(phrase in body_text.lower() for phrase in [
        'this is an automated',
        'do not reply',
        'noreply',
        'automatically generated',
        'undelivered mail'
    ]):
        logger.info(f"Skipping automated email from {msg.from_email}")
        return False
    
    # If we get here, it looks like a legitimate user email
    logger.info(f"Email from {msg.from_email} passed filtering checks")
    return True


def check_inbox_job(config: Config, dry_run: bool = False) -> None:
    """Check inbox for new commands."""
    logger.info("Checking inbox for new messages")
    
    try:
        messages = imap_fetch_unseen(config)
        for msg in messages:
            process_inbound_email(config, msg, dry_run)
            
    except Exception as e:
        logger.error(f"Error checking inbox: {e}")


def list_subscribers() -> None:
    """List current weather subscribers (CLI command)."""
    conn = sqlite3.connect("app.db")
    try:
        subscribers = conn.execute("""
            SELECT email, location, lat, lon, COALESCE(personality, 'neutral') as personality, updated_at 
            FROM subscribers 
            ORDER BY updated_at DESC
        """).fetchall()
        
        print(f"\n📊 Weather Subscribers ({len(subscribers)} total):")
        print("-" * 90)
        
        for email_addr, location, lat, lon, personality, updated_at in subscribers:
            coords = f"({lat:.4f}, {lon:.4f})" if lat and lon else "(no coordinates)"
            print(f"{email_addr:<30} {location:<25} {coords:<20} [{personality}]")
            
    finally:
        conn.close()


def list_reminders() -> None:
    """List pending reminders (CLI command)."""
    conn = sqlite3.connect("app.db")
    try:
        reminders = conn.execute("""
            SELECT email, message, first_run_at, remaining_repeats, last_sent_at
            FROM reminders 
            ORDER BY first_run_at
        """).fetchall()
        
        print(f"\n📅 Pending Reminders ({len(reminders)} total):")
        print("-" * 100)
        
        for email_addr, message, first_run_at, remaining_repeats, last_sent_at in reminders:
            status = f"{remaining_repeats} left" if last_sent_at else "pending"
            print(f"{email_addr:<30} {first_run_at:<20} {status:<10} {message}")
            
    finally:
        conn.close()


def send_test_email(config: Config, to_email: str) -> None:
    """Send a test email (CLI command)."""
    subject = "Daily Brief Service - Test Email"
    body = f"✅ Test email sent successfully at {datetime.now().isoformat()}\n\n"
    body += "This confirms your email configuration is working.\n\n"
    body += _get_usage_footer()
    
    if send_email(config, to_email, subject, body):
        print(f"✅ Test email sent to {to_email}")
    else:
        print(f"❌ Failed to send test email to {to_email}")


def create_readme_if_missing() -> None:
    """Create README.md if it doesn't exist."""
    if not os.path.exists("README.md"):
        readme_content = """# Daily Brief Service

Email-driven weather subscriptions and calendar reminders service.

## Features

- **Weather Subscriptions**: Send daily weather forecasts at 05:00 local time
- **Calendar Reminders**: Schedule one-time or repeating reminders via email
- **Free APIs**: Uses Open-Meteo for weather data (no API key required)
- **Simple Commands**: Send plain text emails to interact with the service

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment variables:
   ```bash
   export EMAIL_ADDRESS="your-service-email@example.com"
   export EMAIL_PASSWORD="your-app-password"
   export IMAP_HOST="imap.example.com"
   export IMAP_PORT="993"
   export SMTP_HOST="smtp.example.com" 
   export SMTP_PORT="587"
   export SMTP_USE_TLS="true"
   export TZ="Europe/Bratislava"
   ```

3. Run the service:
   ```bash
   python app.py
   ```

## Usage

Send emails to your configured service address:

### Weather Subscriptions
- Send location: `Prague, CZ` or `New York, NY`
- Send `delete` to unsubscribe

### Calendar Reminders
Send structured message:
```
date=2025-12-01
time=08:30
message=Doctor Appointment
repeat=3
```

### CLI Commands
- `python app.py --list-subs` - List weather subscribers
- `python app.py --list-reminders` - List pending reminders
- `python app.py --send-test user@example.com` - Send test email
- `python app.py --dry-run` - Run without sending emails

## License

Open source - use freely.
"""
        
        with open("README.md", "w") as f:
            f.write(readme_content)
        logger.info("Created README.md file")


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(description="Daily Brief Service")
    parser.add_argument("--dry-run", action="store_true", help="Run without sending emails")
    parser.add_argument("--list-subs", action="store_true", help="List weather subscribers")
    parser.add_argument("--list-reminders", action="store_true", help="List pending reminders")
    parser.add_argument("--send-test", metavar="EMAIL", help="Send test email to address")
    
    args = parser.parse_args()
    
    # Create README on first run
    create_readme_if_missing()
    
    # Initialize database
    init_db()
    
    # Handle CLI commands
    if args.list_subs:
        list_subscribers()
        return
        
    if args.list_reminders:
        list_reminders()
        return
    
    if args.send_test:
        config = load_env()
        send_test_email(config, args.send_test)
        return
    
    # Start main service
    logger.info("Starting Daily Brief Service")
    config = load_env()
    
    if args.dry_run:
        logger.info("Running in DRY RUN mode - no emails will be sent")
    
    # Initialize scheduler
    global scheduler
    scheduler = BlockingScheduler(timezone=config.timezone)
    
    # Schedule jobs
    scheduler.add_job(
        func=lambda: check_inbox_job(config, args.dry_run),
        trigger=IntervalTrigger(minutes=1),
        id='check_inbox',
        name='Check inbox for new commands'
    )
    
    # Reminder system temporarily disabled
    # scheduler.add_job(
    #     func=lambda: run_due_reminders_job(config, args.dry_run),
    #     trigger=IntervalTrigger(minutes=1),
    #     id='check_reminders',
    #     name='Send due calendar reminders'
    # )
    
    scheduler.add_job(
        func=lambda: run_daily_weather_job(config, args.dry_run),
        trigger=CronTrigger(hour=5, minute=0, timezone=config.timezone),
        id='daily_weather',
        name='Send daily weather forecasts'
    )
    
    logger.info("Scheduler started - Daily Brief Service is running")
    logger.info("Jobs scheduled:")
    logger.info("  - Check inbox: every 1 minute")
    # logger.info("  - Check reminders: every 1 minute")  # Disabled
    logger.info("  - Daily weather: 05:00 Bratislava time")
    
    logger.info("🎯 Press Ctrl+C to stop the service gracefully")
    
    try:
        scheduler.start()
    except KeyboardInterrupt:
        # This should be handled by signal_handler, but keeping as fallback
        logger.info("🛑 Keyboard interrupt received")
        signal_handler(signal.SIGINT, None)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        if scheduler and scheduler.running:
            scheduler.shutdown()
        raise


if __name__ == "__main__":
    main()