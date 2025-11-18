from flask import Flask

def create_app():
    app = Flask(__name__)
    # TODO: Add all route and config setup here
    return app
#!/usr/bin/env python3
"""
Secure Flask Web Interface for Daily Brief Service
Copyright (c) 2025 Filip Johanes. All Rights Reserved.

Security features:
- CSRF protection
- Rate limiting
- Input validation & sanitization
- SQL injection prevention
- XSS protection
- Secure headers
"""

import os
import sys
import sqlite3
import logging
import secrets
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional, Dict

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_wtf import FlaskForm, CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from wtforms import StringField, SelectField, SubmitField, validators
from wtforms.validators import DataRequired, Email, Length, ValidationError
from email_validator import validate_email, EmailNotValidError

# Load environment variables FIRST before importing app
from dotenv import load_dotenv
load_dotenv()

# Import from existing app.py
sys.path.insert(0, os.path.dirname(__file__))
from app import (
    geocode_location, get_weather_forecast, 
    generate_weather_summary, Config
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),
        logging.FileHandler('web_app.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Security configuration
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(32))
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = None  # CSRF tokens don't expire
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True if using HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024  # 16KB max request size

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Initialize rate limiter (prevent DDoS/spam)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Initialize config
try:
    service_config = Config()
except Exception as e:
    logger.error(f"Failed to load service config: {e}")
    service_config = None


# Custom validators
def validate_location_format(form, field):
    """Validate location input for security."""
    location = field.data.strip()
    
    # Length check
    if len(location) < 2:
        raise ValidationError('Location must be at least 2 characters')
    if len(location) > 100:
        raise ValidationError('Location is too long (max 100 characters)')
    
    # Block suspicious patterns (SQL injection attempts)
    suspicious_patterns = [
        'select ', 'insert ', 'update ', 'delete ', 'drop ',
        'union ', '--', '/*', '*/', 'xp_', 'exec ', 'script'
    ]
    location_lower = location.lower()
    for pattern in suspicious_patterns:
        if pattern in location_lower:
            raise ValidationError('Invalid location format')
    
    # Allow only letters, numbers, spaces, commas, dashes, dots
    import re
    if not re.match(r'^[a-zA-Z0-9\s,.\-áéíóúñüÁÉÍÓÚÑÜčďěňřšťůýžČĎĚŇŘŠŤŮÝŽ]+$', location):
        raise ValidationError('Location contains invalid characters')


# Forms with security
class SubscribeForm(FlaskForm):
    """Secure subscription form with validation."""
    email = StringField('Email Address', [
        DataRequired(message='Email is required'),
        Email(message='Invalid email address'),
        Length(min=5, max=100, message='Email must be 5-100 characters')
    ])
    
    location = StringField('Location', [
        DataRequired(message='Location is required'),
        validate_location_format
    ])
    
    language = SelectField('Language', choices=[
        ('en', 'English'),
        ('es', 'Español (Spanish)'),
        ('sk', 'Slovenčina (Slovak)')
    ], validators=[DataRequired()])
    
    personality = SelectField('Personality Mode', choices=[
        ('neutral', 'Neutral - Standard reports'),
        ('cute', 'Cute - Friendly & emoji-rich'),
        ('brutal', 'Brutal - Blunt & direct')
    ], validators=[DataRequired()])
    
    submit = SubmitField('Subscribe')
    
    def validate_email(self, field):
        """Additional email validation."""
        try:
            # Validate email using email-validator library
            valid = validate_email(field.data, check_deliverability=False)
            field.data = valid.normalized  # Normalize email
        except EmailNotValidError as e:
            raise ValidationError(f'Invalid email: {str(e)}')
    
    def validate(self, extra_validators=None):
        """Custom validation logic."""
        if not super().validate(extra_validators):
            return False
        
        # Emuska only works with Slovak language
        if self.personality.data == 'emuska' and self.language.data != 'sk':
            self.personality.errors.append(
                'Emuska personality is only available in Slovak language'
            )
            return False
        
        return True


class UnsubscribeForm(FlaskForm):
    """Secure unsubscribe form."""
    email = StringField('Email Address', [
        DataRequired(message='Email is required'),
        Email(message='Invalid email address')
    ])
    submit = SubmitField('Unsubscribe')


def get_db_connection():
    """Get secure database connection with read-only where appropriate."""
    conn = sqlite3.connect('app.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def sanitize_output(text: str) -> str:
    """Sanitize text output to prevent XSS."""
    import html
    return html.escape(str(text))


@app.route('/')
@limiter.limit("30 per minute")
def index():
    """Home page."""
    return render_template('index.html')


@app.route('/subscribe', methods=['GET', 'POST'])
@limiter.limit("10 per minute")  # Stricter limit for submissions
def subscribe():
    """Secure subscription page."""
    form = SubscribeForm()
    
    if form.validate_on_submit():
        try:
            # Sanitize inputs (already validated by form)
            email = form.email.data.strip().lower()
            location = form.location.data.strip()
            language = form.language.data
            personality = form.personality.data
            
            # Geocode location
            logger.info(f"Processing subscription for {email} - {location}")
            geocode_result = geocode_location(location)
            
            if not geocode_result:
                flash('Could not find that location. Please try a more specific address (e.g., "Bratislava, Slovakia")', 'error')
                return render_template('subscribe.html', form=form)
            
            lat, lon, display_name, timezone_str = geocode_result
            
            # Save to database with parameterized query (SQL injection safe)
            conn = get_db_connection()
            try:
                # Check if already subscribed
                existing = conn.execute(
                    'SELECT email FROM subscribers WHERE email = ?', 
                    (email,)
                ).fetchone()
                
                if existing:
                    # Update existing subscription
                    conn.execute("""
                        UPDATE subscribers 
                        SET location = ?, lat = ?, lon = ?, timezone = ?, personality = ?, 
                            language = ?, updated_at = ?
                        WHERE email = ?
                    """, (display_name, lat, lon, timezone_str, personality, language, 
                          datetime.now(ZoneInfo(service_config.timezone)).isoformat(), email))
                    action = 'updated'
                else:
                    # Insert new subscription
                    conn.execute("""
                        INSERT INTO subscribers (email, location, lat, lon, timezone, personality, language, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (email, display_name, lat, lon, timezone_str, personality, language,
                          datetime.now(ZoneInfo(service_config.timezone)).isoformat()))
                    action = 'created'
                
                conn.commit()
                logger.info(f"Subscription {action} for {email} in timezone {timezone_str}")
                
                flash(f'✅ Successfully subscribed to daily weather for {sanitize_output(display_name)} (emails at 05:00 {timezone_str})!', 'success')
                return redirect(url_for('preview', email=email))
                
            except sqlite3.Error as e:
                logger.error(f"Database error: {e}")
                flash('An error occurred. Please try again later.', 'error')
            finally:
                conn.close()
        
        except Exception as e:
            logger.error(f"Subscription error: {e}")
            flash('An unexpected error occurred. Please try again.', 'error')
    
    return render_template('subscribe.html', form=form)


@app.route('/unsubscribe', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def unsubscribe():
    """Secure unsubscribe page."""
    form = UnsubscribeForm()
    
    if form.validate_on_submit():
        try:
            email = form.email.data.strip().lower()
            
            conn = get_db_connection()
            try:
                cursor = conn.execute('DELETE FROM subscribers WHERE email = ?', (email,))
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"Unsubscribed: {email}")
                    flash(f'✅ Successfully unsubscribed {sanitize_output(email)} from daily weather.', 'success')
                else:
                    flash(f'Email {sanitize_output(email)} was not found in our system.', 'info')
            
            except sqlite3.Error as e:
                logger.error(f"Database error during unsubscribe: {e}")
                flash('An error occurred. Please try again later.', 'error')
            finally:
                conn.close()
        
        except Exception as e:
            logger.error(f"Unsubscribe error: {e}")
            flash('An unexpected error occurred. Please try again.', 'error')
    
    return render_template('unsubscribe.html', form=form)


@app.route('/preview')
@limiter.limit("20 per minute")
def preview():
    """Preview weather email for a subscriber."""
    email = request.args.get('email', '').strip().lower()
    
    if not email:
        flash('Email parameter is required', 'error')
        return redirect(url_for('index'))
    
    try:
        # Validate email format (security check)
        validate_email(email, check_deliverability=False)
    except EmailNotValidError:
        flash('Invalid email format', 'error')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    try:
        # Parameterized query (SQL injection safe)
        subscriber = conn.execute("""
            SELECT email, location, lat, lon, COALESCE(timezone, 'UTC') as timezone, personality, language 
            FROM subscribers WHERE email = ?
        """, (email,)).fetchone()
        
        if not subscriber:
            flash('Subscriber not found', 'error')
            return redirect(url_for('subscribe'))
        
        # Get weather forecast using subscriber's timezone
        weather = get_weather_forecast(
            subscriber['lat'], 
            subscriber['lon'], 
            subscriber['timezone']
        )
        
        if weather:
            summary = generate_weather_summary(
                weather,
                subscriber['location'],
                subscriber['personality'],
                subscriber['language']
            )
        else:
            summary = "Unable to fetch weather data at this time."
        
        return render_template('preview.html', 
                             subscriber=subscriber,
                             weather_summary=summary)
    
    except Exception as e:
        logger.error(f"Preview error: {e}")
        flash('An error occurred loading the preview', 'error')
        return redirect(url_for('index'))
    finally:
        conn.close()


@app.route('/stats')
@limiter.limit("20 per minute")
def stats():
    """Public statistics page (no sensitive data)."""
    conn = get_db_connection()
    try:
        # Get aggregate statistics (include all users in totals, but hide special personality)
        total_subscribers = conn.execute('SELECT COUNT(*) as count FROM subscribers').fetchone()['count']
        
        language_stats = conn.execute("""
            SELECT language, COUNT(*) as count 
            FROM subscribers 
            GROUP BY language
        """).fetchall()
        
        personality_stats = conn.execute("""
            SELECT personality, COUNT(*) as count 
            FROM subscribers 
            WHERE personality != 'emuska'
            GROUP BY personality
        """).fetchall()
        
        return render_template('stats.html',
                             total=total_subscribers,
                             languages=language_stats,
                             personalities=personality_stats)
    
    except Exception as e:
        logger.error(f"Stats error: {e}")
        flash('Unable to load statistics', 'error')
        return redirect(url_for('index'))
    finally:
        conn.close()


# API endpoints (optional, but secure)
@app.route('/api/check-email', methods=['POST'])
@limiter.limit("20 per minute")
@csrf.exempt  # For API calls, but we still validate
def api_check_email():
    """API to check if email is subscribed (rate limited)."""
    try:
        data = request.get_json()
        if not data or 'email' not in data:
            return jsonify({'error': 'Email required'}), 400
        
        email = data['email'].strip().lower()
        
        # Validate email
        try:
            validate_email(email, check_deliverability=False)
        except EmailNotValidError:
            return jsonify({'error': 'Invalid email format'}), 400
        
        conn = get_db_connection()
        try:
            subscriber = conn.execute(
                'SELECT email, location, personality, language FROM subscribers WHERE email = ?',
                (email,)
            ).fetchone()
            
            if subscriber:
                return jsonify({
                    'subscribed': True,
                    'location': subscriber['location'],
                    'personality': subscriber['personality'],
                    'language': subscriber['language']
                })
            else:
                return jsonify({'subscribed': False})
        
        finally:
            conn.close()
    
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# Error handlers
@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', 
                         error_code=404,
                         error_message='Page not found'), 404


@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template('error.html',
                         error_code=429,
                         error_message='Too many requests. Please slow down.'), 429


@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal error: {e}")
    return render_template('error.html',
                         error_code=500,
                         error_message='Internal server error'), 500


# Security headers
@app.after_request
def set_security_headers(response):
    """Add security headers to all responses."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self' 'unsafe-inline'"
    return response


if __name__ == '__main__':
    # Development server (use systemd + gunicorn for production)
    logger.info("Starting Daily Brief Web Interface")
    logger.info("🔒 Security features enabled: CSRF, Rate Limiting, Input Validation")
    
    # Generate secret key if not set
    if not os.getenv('FLASK_SECRET_KEY'):
        secret = secrets.token_hex(32)
        logger.warning(f"⚠️ FLASK_SECRET_KEY not set! Generated temporary key")
        logger.warning(f"Add to .env: FLASK_SECRET_KEY={secret}")
    
    app.run(
        host='0.0.0.0',  # Listen on all interfaces
        port=5000,
        debug=False  # Never use debug=True in production!
    )
