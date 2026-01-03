#!/usr/bin/env python3
"""
REST API for Daily Brief Service
Exposes database operations for remote web frontend access.
"""

import os
import sqlite3
import secrets
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from services.user_service import register_user, authenticate_user, get_user_by_email, hash_password
from services.subscription_service import add_or_update_subscriber, delete_subscriber
from services.weather_service import geocode_location, get_weather_forecast, generate_weather_summary
from services.countdown_service import add_countdown, CountdownEvent

load_dotenv()

app = Flask(__name__)

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["500 per hour"],
    storage_uri="memory://"
)

# API Key Authentication
API_KEYS = set(os.getenv('API_KEYS', '').split(','))
if not API_KEYS or API_KEYS == {''}:
    # Generate a default key for development (should be set in production)
    default_key = secrets.token_urlsafe(32)
    API_KEYS = {default_key}
    print(f"⚠️ WARNING: No API_KEYS set in environment!")
    print(f"⚠️ Generated temporary API key: {default_key}")
    print(f"⚠️ Add to .env: API_KEYS={default_key}")


def get_db_path():
    return os.getenv("APP_DB_PATH", "app.db")


def require_api_key(f):
    """Decorator to require valid API key."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key not in API_KEYS:
            return jsonify({'error': 'Invalid or missing API key'}), 401
        return f(*args, **kwargs)
    return decorated_function


# Health check endpoint (no auth required)
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'service': 'dailybrief-api'})


# ==================== USER ENDPOINTS ====================

@app.route('/api/users/register', methods=['POST'])
@limiter.limit("10 per hour")
@require_api_key
def api_register_user():
    """Register a new user."""
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    nickname = (data.get('nickname') or '').strip()
    username = (data.get('username') or '').strip()
    email_consent = data.get('email_consent', False)
    terms_accepted = data.get('terms_accepted', False)
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    success, message = register_user(
        email=email,
        password=password,
        nickname=nickname,
        username=username,
        email_consent=email_consent,
        terms_accepted=terms_accepted
    )
    
    if success:
        return jsonify({'success': True, 'message': message}), 201
    else:
        return jsonify({'success': False, 'error': message}), 400


@app.route('/api/users/authenticate', methods=['POST'])
@limiter.limit("20 per hour")
@require_api_key
def api_authenticate_user():
    """Authenticate a user."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    user = authenticate_user(email, password)
    if user:
        return jsonify({'success': True, 'user': user}), 200
    else:
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401


@app.route('/api/users/<email>', methods=['GET'])
@limiter.limit("100 per hour")
@require_api_key
def api_get_user(email):
    """Get user data by email."""
    email = email.strip().lower()
    user = get_user_by_email(email)
    
    if user:
        return jsonify({'success': True, 'user': user}), 200
    else:
        return jsonify({'success': False, 'error': 'User not found'}), 404


@app.route('/api/users/<email>/password', methods=['PUT'])
@limiter.limit("10 per hour")
@require_api_key
def api_update_password(email):
    """Update user password."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    new_password = data.get('new_password', '')
    if not new_password:
        return jsonify({'error': 'New password required'}), 400
    
    email = email.strip().lower()
    hashed_pw = hash_password(new_password)
    
    conn = sqlite3.connect(get_db_path())
    try:
        conn.execute("UPDATE users SET password_hash = ? WHERE email = ?", (hashed_pw, email))
        conn.commit()
        if conn.total_changes > 0:
            return jsonify({'success': True, 'message': 'Password updated'}), 200
        else:
            return jsonify({'success': False, 'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/api/users/<email>/nickname', methods=['PUT'])
@limiter.limit("20 per hour")
@require_api_key
def api_update_nickname(email):
    """Update user nickname."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    nickname = data.get('nickname', '').strip()
    if not nickname:
        return jsonify({'error': 'Nickname required'}), 400
    
    email = email.strip().lower()
    
    conn = sqlite3.connect(get_db_path())
    try:
        conn.execute("UPDATE users SET nickname = ? WHERE email = ?", (nickname, email))
        conn.commit()
        if conn.total_changes > 0:
            return jsonify({'success': True, 'message': 'Nickname updated'}), 200
        else:
            return jsonify({'success': False, 'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


# ==================== WEATHER SUBSCRIPTION ENDPOINTS ====================

@app.route('/api/weather/subscriptions/<email>', methods=['GET'])
@limiter.limit("100 per hour")
@require_api_key
def api_get_weather_subscription(email):
    """Get weather subscription by email."""
    email = email.strip().lower()
    
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    try:
        subscriber = conn.execute("""
            SELECT ws.email, ws.location, ws.lat, ws.lon, 
                   COALESCE(u.timezone, 'UTC') as timezone, 
                   ws.personality, ws.language 
            FROM weather_subscriptions ws
            JOIN users u ON ws.email = u.email
            WHERE ws.email = ? AND u.weather_enabled = 1
        """, (email,)).fetchone()
        
        if subscriber:
            return jsonify({
                'success': True,
                'subscription': dict(subscriber)
            }), 200
        else:
            return jsonify({'success': False, 'error': 'Subscription not found'}), 404
    finally:
        conn.close()


@app.route('/api/weather/subscriptions', methods=['POST'])
@limiter.limit("20 per hour")
@require_api_key
def api_create_weather_subscription():
    """Create or update weather subscription."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    email = data.get('email', '').strip().lower()
    location = data.get('location', '').strip()
    personality = data.get('personality', 'neutral')
    language = data.get('language', 'en')
    
    if not email or not location:
        return jsonify({'error': 'Email and location required'}), 400
    
    # Geocode location
    geocode_result = geocode_location(location)
    if not geocode_result:
        return jsonify({'error': 'Invalid location or geocoding failed'}), 400
    
    lat, lon, display_name, timezone_str = geocode_result
    
    try:
        add_or_update_subscriber(email, display_name, lat, lon, personality, language, timezone_str)
        return jsonify({
            'success': True,
            'message': 'Subscription created/updated',
            'location': display_name
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/weather/subscriptions/<email>', methods=['PUT'])
@limiter.limit("20 per hour")
@require_api_key
def api_update_weather_subscription(email):
    """Update weather subscription."""
    return api_create_weather_subscription()  # Same logic as create


@app.route('/api/weather/subscriptions/<email>', methods=['DELETE'])
@limiter.limit("20 per hour")
@require_api_key
def api_delete_weather_subscription(email):
    """Delete weather subscription."""
    email = email.strip().lower()
    
    try:
        deleted = delete_subscriber(email)
        if deleted > 0:
            return jsonify({'success': True, 'message': 'Subscription deleted'}), 200
        else:
            return jsonify({'success': False, 'error': 'Subscription not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/weather/preview/<email>', methods=['GET'])
@limiter.limit("50 per hour")
@require_api_key
def api_preview_weather(email):
    """Get weather preview for user."""
    email = email.strip().lower()
    
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    try:
        subscriber = conn.execute("""
            SELECT ws.email, ws.location, ws.lat, ws.lon, 
                   COALESCE(u.timezone, 'UTC') as timezone, 
                   ws.personality, ws.language 
            FROM weather_subscriptions ws
            JOIN users u ON ws.email = u.email
            WHERE ws.email = ?
        """, (email,)).fetchone()
        
        if not subscriber:
            return jsonify({'error': 'Subscription not found'}), 404
        
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
            return jsonify({
                'success': True,
                'subscriber': dict(subscriber),
                'weather_summary': summary
            }), 200
        else:
            return jsonify({'error': 'Unable to fetch weather data'}), 500
    finally:
        conn.close()


# ==================== COUNTDOWN ENDPOINTS ====================

@app.route('/api/countdowns/<email>', methods=['GET'])
@limiter.limit("100 per hour")
@require_api_key
def api_get_countdowns(email):
    """Get all countdowns for a user."""
    email = email.strip().lower()
    
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    try:
        countdowns = conn.execute("""
            SELECT id, name, date, yearly, message_before, message_after, created_at
            FROM countdowns WHERE email = ?
            ORDER BY date
        """, (email,)).fetchall()
        
        return jsonify({
            'success': True,
            'countdowns': [dict(row) for row in countdowns]
        }), 200
    finally:
        conn.close()


@app.route('/api/countdowns', methods=['POST'])
@limiter.limit("50 per hour")
@require_api_key
def api_create_countdown():
    """Create a new countdown."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    email = data.get('email', '').strip().lower()
    name = data.get('name', '').strip()
    date = data.get('date', '').strip()
    yearly = data.get('yearly', False)
    message_before = data.get('message_before', '')
    message_after = data.get('message_after', '')
    
    if not email or not name or not date:
        return jsonify({'error': 'Email, name, and date required'}), 400
    
    try:
        countdown = CountdownEvent(name, date, yearly, message_before, message_after)
        add_countdown(email, countdown)
        return jsonify({
            'success': True,
            'message': 'Countdown created'
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/countdowns/<int:countdown_id>', methods=['PUT'])
@limiter.limit("50 per hour")
@require_api_key
def api_update_countdown(countdown_id):
    """Update a countdown."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    name = data.get('name', '').strip()
    date = data.get('date', '').strip()
    yearly = data.get('yearly', False)
    message_before = data.get('message_before', '')
    
    conn = sqlite3.connect(get_db_path())
    try:
        conn.execute("""
            UPDATE countdowns 
            SET name = ?, date = ?, yearly = ?, message_before = ?
            WHERE id = ?
        """, (name, date, int(yearly), message_before, countdown_id))
        conn.commit()
        
        if conn.total_changes > 0:
            return jsonify({'success': True, 'message': 'Countdown updated'}), 200
        else:
            return jsonify({'success': False, 'error': 'Countdown not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/api/countdowns/<int:countdown_id>', methods=['DELETE'])
@limiter.limit("50 per hour")
@require_api_key
def api_delete_countdown(countdown_id):
    """Delete a countdown."""
    conn = sqlite3.connect(get_db_path())
    try:
        cursor = conn.execute('DELETE FROM countdowns WHERE id = ?', (countdown_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            return jsonify({'success': True, 'message': 'Countdown deleted'}), 200
        else:
            return jsonify({'success': False, 'error': 'Countdown not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


# ==================== STATS ENDPOINTS ====================

@app.route('/api/stats', methods=['GET'])
@limiter.limit("100 per hour")
@require_api_key
def api_get_stats():
    """Get public statistics."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    try:
        total_subscribers = conn.execute("""
            SELECT COUNT(*) as count FROM users WHERE weather_enabled = 1
        """).fetchone()['count']
        
        language_stats = conn.execute("""
            SELECT ws.language, COUNT(*) as count 
            FROM weather_subscriptions ws
            JOIN users u ON ws.email = u.email
            WHERE u.weather_enabled = 1
            GROUP BY ws.language
        """).fetchall()
        
        personality_stats = conn.execute("""
            SELECT ws.personality, COUNT(*) as count 
            FROM weather_subscriptions ws
            JOIN users u ON ws.email = u.email
            WHERE u.weather_enabled = 1 AND ws.personality != 'emuska'
            GROUP BY ws.personality
        """).fetchall()
        
        return jsonify({
            'success': True,
            'total_subscribers': total_subscribers,
            'languages': [dict(row) for row in language_stats],
            'personalities': [dict(row) for row in personality_stats]
        }), 200
    finally:
        conn.close()


# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'Rate limit exceeded'}), 429


@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("🚀 Starting Daily Brief REST API")
    print(f"📊 Database: {get_db_path()}")
    print("🔐 API Key authentication enabled")
    
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('API_PORT', '5001')),
        debug=False
    )
