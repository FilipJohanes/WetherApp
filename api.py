#!/usr/bin/env python3
"""
REST API for Daily Brief Service
Exposes database operations for remote web frontend access.
"""

import os
import sqlite3
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from services.user_service import register_user, authenticate_user, get_user_by_email, hash_password
from services.subscription_service import add_or_update_subscriber, delete_subscriber
from services.weather_service import geocode_location, get_weather_forecast, generate_weather_summary
from services.countdown_service import add_countdown, CountdownEvent
from services.email_service import send_email

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


def init_api_db():
    """Initialize database with all necessary tables including password reset."""
    db_path = get_db_path()
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"⚠️ Database not found at {db_path}")
        print("🔧 Initializing database...")
    
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    
    try:
        # Create users table if not exists
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                username TEXT,
                nickname TEXT,
                password_hash TEXT,
                timezone TEXT DEFAULT 'UTC',
                lat REAL,
                lon REAL,
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
        
        # Create weather_subscriptions table if not exists
        conn.execute("""
            CREATE TABLE IF NOT EXISTS weather_subscriptions (
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
        
        # Create countdowns table if not exists
        conn.execute("""
            CREATE TABLE IF NOT EXISTS countdowns (
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
        
        # Create password_reset_tokens table if not exists
        conn.execute("""
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                token TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                used INTEGER DEFAULT 0,
                FOREIGN KEY (email) REFERENCES users(email)
            )
        """)
        
        # Create indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_reset_token ON password_reset_tokens(token)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_reset_email ON password_reset_tokens(email)")
        
        conn.commit()
        print("✅ Database initialized successfully")
        
    except sqlite3.Error as e:
        print(f"❌ Database initialization error: {e}")
        raise
    finally:
        conn.close()


def cleanup_expired_tokens():
    """Delete expired and old used password reset tokens."""
    conn = sqlite3.connect(get_db_path())
    try:
        # Delete tokens that expired more than 24 hours ago (for audit trail)
        expired_cutoff = datetime.now() - timedelta(hours=24)
        
        cursor = conn.execute("""
            DELETE FROM password_reset_tokens 
            WHERE datetime(expires_at) < datetime(?)
        """, (expired_cutoff,))
        
        expired_count = cursor.rowcount
        
        # Delete used tokens older than 7 days (keep recent for audit)
        used_cutoff = datetime.now() - timedelta(days=7)
        
        cursor = conn.execute("""
            DELETE FROM password_reset_tokens 
            WHERE used = 1 AND datetime(created_at) < datetime(?)
        """, (used_cutoff,))
        
        used_count = cursor.rowcount
        
        conn.commit()
        
        if expired_count > 0 or used_count > 0:
            print(f"🧹 Cleaned up {expired_count} expired and {used_count} old used password reset tokens")
        
    except Exception as e:
        print(f"❌ Token cleanup error: {e}")
    finally:
        conn.close()


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
        print("❌ Registration error: No data provided")
        return jsonify({'error': 'No data provided'}), 400
    
    print(f"📝 Registration request data: {data}")
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    nickname = (data.get('nickname') or '').strip()
    username = (data.get('username') or '').strip()
    email_consent = data.get('email_consent', False)
    terms_accepted = data.get('terms_accepted', False)
    
    print(f"📧 Email: {email}, Nickname: {nickname}, Username: {username}")
    
    if not email or not password:
        print(f"❌ Registration error: Missing email or password")
        return jsonify({'error': 'Email and password required'}), 400
    
    success, message = register_user(
        email=email,
        password=password,
        nickname=nickname,
        username=username,
        email_consent=email_consent,
        terms_accepted=terms_accepted
    )
    
    print(f"✅ Registration result: success={success}, message={message}")
    
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


@app.route('/api/users/password-reset-request', methods=['POST'])
@limiter.limit("5 per hour")
@require_api_key
def api_request_password_reset():
    """Request a password reset email."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    email = data.get('email', '').strip().lower()
    if not email:
        return jsonify({'error': 'Email required'}), 400
    
    # Check if user exists
    user = get_user_by_email(email)
    if not user:
        # Don't reveal if email exists or not (security best practice)
        return jsonify({'success': True, 'message': 'If the email exists, a reset link will be sent'}), 200
    
    # Generate secure token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=1)  # Token valid for 1 hour
    
    # Store token in database
    conn = sqlite3.connect(get_db_path())
    try:
        # Delete any existing unused tokens for this email
        conn.execute("DELETE FROM password_reset_tokens WHERE email = ? AND used = 0", (email,))
        
        # Insert new token
        conn.execute("""
            INSERT INTO password_reset_tokens (email, token, expires_at)
            VALUES (?, ?, ?)
        """, (email, token, expires_at))
        conn.commit()
        
        # Get web app URL from environment
        web_url = os.getenv('WEB_APP_URL', 'http://localhost:5000')
        reset_link = f"{web_url}/reset-password/{token}"
        
        # Send email with reset link
        subject = "Password Reset Request - Daily Brief"
        body = f"""Hello,

You requested a password reset for your Daily Brief account.

Click the link below to reset your password:
{reset_link}

This link will expire in 1 hour.

If you didn't request this, please ignore this email.

Best regards,
Daily Brief Team
"""
        
        try:
            send_email(email, subject, body)
            print(f"✉️ Password reset email sent to {email}")
        except Exception as e:
            print(f"❌ Failed to send password reset email: {e}")
            # Still return success to not reveal if email exists
        
        return jsonify({'success': True, 'message': 'If the email exists, a reset link will be sent'}), 200
        
    except Exception as e:
        print(f"❌ Password reset request error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        conn.close()


@app.route('/api/users/password-reset', methods=['POST'])
@limiter.limit("10 per hour")
@require_api_key
def api_reset_password():
    """Reset password using token."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    token = data.get('token', '').strip()
    new_password = data.get('new_password', '')
    
    if not token or not new_password:
        return jsonify({'error': 'Token and new password required'}), 400
    
    # Validate token
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    try:
        reset_token = conn.execute("""
            SELECT email, expires_at, used
            FROM password_reset_tokens
            WHERE token = ?
        """, (token,)).fetchone()
        
        if not reset_token:
            return jsonify({'error': 'Invalid or expired token'}), 400
        
        if reset_token['used']:
            return jsonify({'error': 'Token already used'}), 400
        
        # Check if token expired
        expires_at = datetime.fromisoformat(reset_token['expires_at'])
        if datetime.now() > expires_at:
            return jsonify({'error': 'Token expired'}), 400
        
        # Update password
        email = reset_token['email']
        hashed_pw = hash_password(new_password)
        
        conn.execute("UPDATE users SET password_hash = ? WHERE email = ?", (hashed_pw, email))
        
        # Mark token as used
        conn.execute("UPDATE password_reset_tokens SET used = 1 WHERE token = ?", (token,))
        
        conn.commit()
        
        print(f"✅ Password reset successful for {email}")
        
        return jsonify({'success': True, 'message': 'Password updated successfully'}), 200
        
    except Exception as e:
        print(f"❌ Password reset error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
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
    
    # Initialize database (creates tables if they don't exist)
    init_api_db()
    
    # Clean up expired password reset tokens
    cleanup_expired_tokens()
    
    print("🔐 API Key authentication enabled")
    
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('API_PORT', '5001')),
        debug=False
    )
