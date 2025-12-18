# --- All imports at the top, deduplicated and complete ---
import os
import sys
import sqlite3
import logging
import secrets
import re
import html
from datetime import datetime
from zoneinfo import ZoneInfo
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_wtf import FlaskForm, CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from wtforms import StringField, SelectField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length, ValidationError, EqualTo
from email_validator import validate_email, EmailNotValidError
from dotenv import load_dotenv
from services.weather_service import geocode_location, get_weather_forecast, generate_weather_summary
from app import Config
from services.countdown_service import add_countdown, CountdownEvent
from services.user_service import register_user, authenticate_user, get_user_by_email
from functools import wraps

# Load environment variables FIRST before importing app
load_dotenv()

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
    if not re.match(r'^[a-zA-Z0-9\s,.\-áéíóúñüÁÉÍÓÚÑÜčďěňřšťůýžČĎĚŇŘŠŤŮÝŽ]+$', location):
        raise ValidationError('Location contains invalid characters')


# Forms with security
class SubscribeForm(FlaskForm):
    """Secure subscription form with validation."""
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
    
    subscribe_weather = SubmitField('Subscribe to Weather')
    subscribe_countdown = SubmitField('Subscribe to Countdown')
    countdown_name = StringField('Countdown Name')
    countdown_date = StringField('Countdown Date')
    countdown_yearly = StringField('Countdown Yearly')
    countdown_message_before = StringField('Message Before Event')
    countdown_message_after = StringField('Message After Event')
    subscribe_weather = StringField('Subscribe Weather')
    subscribe_countdown = StringField('Subscribe Countdown')
    submit = SubmitField('Subscribe')
    
    def validate_email(self, field):
        """Additional email validation."""
        try:
            # Validate email using email-validator library
            valid = validate_email(field.data, check_deliverability=False)
            field.data = valid.normalized  # Normalize email
        except EmailNotValidError as e:
            raise ValidationError(f'Invalid email: {str(e)}')


class RegistrationForm(FlaskForm):
    """User registration form."""
    email = StringField('Email Address', [
        DataRequired(message='Email is required'),
        Email(message='Invalid email address'),
        Length(min=5, max=100, message='Email must be 5-100 characters')
    ])
    
    nickname = StringField('Nickname (Display Name)', [
        DataRequired(message='Nickname is required'),
        Length(min=2, max=50, message='Nickname must be 2-50 characters')
    ])
    
    password = PasswordField('Password', [
        DataRequired(message='Password is required'),
        Length(min=8, max=128, message='Password must be at least 8 characters')
    ])
    
    password_confirm = PasswordField('Confirm Password', [
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    
    email_consent = BooleanField('I agree to receive emails from Daily Brief Service', [
        DataRequired(message='You must agree to receive emails to use this service')
    ])
    
    terms_accepted = BooleanField('I agree to the Terms and Conditions', [
        DataRequired(message='You must accept the terms and conditions')
    ])
    
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    """User login form."""
    email = StringField('Email Address', [
        DataRequired(message='Email is required'),
        Email(message='Invalid email address')
    ])
    
    password = PasswordField('Password', [
        DataRequired(message='Password is required')
    ])
    
    submit = SubmitField('Login')


class ChangePasswordForm(FlaskForm):
    """Form for changing user password."""
    current_password = PasswordField('Current Password', [
        DataRequired(message='Current password is required')
    ])
    new_password = PasswordField('New Password', [
        DataRequired(message='New password is required'),
        Length(min=8, message='Password must be at least 8 characters')
    ])
    confirm_password = PasswordField('Confirm New Password', [
        DataRequired(message='Please confirm your password'),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')


class ChangeNicknameForm(FlaskForm):
    """Form for changing user nickname."""
    nickname = StringField('Nickname', [
        DataRequired(message='Nickname is required'),
        Length(min=2, max=50, message='Nickname must be 2-50 characters')
    ])
    submit = SubmitField('Update Nickname')


def get_db_connection():
    """Get secure database connection with read-only where appropriate."""
    db_path = os.getenv('APP_DB_PATH', 'app.db')
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def sanitize_output(text: str) -> str:
    """Sanitize text output to prevent XSS."""
    return html.escape(str(text))


def login_required(f):
    """Decorator to require login for certain routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@app.context_processor
def inject_user():
    """Make user data available in all templates."""
    user_email = session.get('user_email')
    user_nickname = session.get('user_nickname')
    user_username = session.get('user_username')
    return dict(
        logged_in=user_email is not None,
        user_email=user_email,
        user_nickname=user_nickname,
        user_username=user_username
    )


@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def register():
    """User registration page."""
    if 'user_email' in session:
        flash('You are already logged in.', 'info')
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        nickname = form.nickname.data.strip()
        password = form.password.data
        email_consent = form.email_consent.data
        terms_accepted = form.terms_accepted.data
        
        success, message = register_user(
            email=email,
            password=password,
            nickname=nickname,
            email_consent=email_consent,
            terms_accepted=terms_accepted
        )
        
        if success:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash(f'Registration failed: {message}', 'error')
    
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    """User login page and AJAX endpoint."""
    if 'user_email' in session:
        return redirect(url_for('index'))
    
    form = LoginForm()
    
    # Handle AJAX login request
    if request.is_json:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password are required'}), 400
        
        user = authenticate_user(email, password)
        if user:
            session['user_email'] = user['email']
            session['user_nickname'] = user['nickname']
            session['user_username'] = user['username']
            session.permanent = False  # Session expires when browser closes
            return jsonify({'success': True, 'message': 'Login successful'})
        else:
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
    
    # Handle regular form submission
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data
        
        user = authenticate_user(email, password)
        if user:
            session['user_email'] = user['email']
            session['user_nickname'] = user['nickname']
            session['user_username'] = user['username']
            session.permanent = False
            flash('Login successful!', 'success')
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    """User logout."""
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))


@app.route('/terms')
def terms():
    """Terms and Conditions page."""
    return render_template('terms.html')


@app.route('/settings', methods=['GET', 'POST'])
@login_required
@limiter.limit("10 per minute")
def settings():
    """User settings page for password and nickname changes."""
    password_form = ChangePasswordForm()
    nickname_form = ChangeNicknameForm()
    
    # Pre-fill nickname form with current nickname
    if request.method == 'GET':
        user_email = session.get('user_email')
        user = get_user_by_email(user_email)
        if user and user.get('nickname'):
            nickname_form.nickname.data = user['nickname']
    
    # Handle password change
    if 'change_password' in request.form and password_form.validate_on_submit():
        user_email = session.get('user_email')
        current_password = password_form.current_password.data
        new_password = password_form.new_password.data
        
        # Verify current password
        user = authenticate_user(user_email, current_password)
        if not user:
            flash('Current password is incorrect.', 'error')
        else:
            # Update password
            from services.user_service import hash_password
            import sqlite3
            
            try:
                conn = get_db_connection()
                hashed_pw = hash_password(new_password)
                conn.execute("UPDATE users SET password_hash = ? WHERE email = ?", (hashed_pw, user_email))
                conn.commit()
                conn.close()
                flash('Password updated successfully!', 'success')
                logger.info(f"Password changed for {user_email}")
            except Exception as e:
                logger.error(f"Password change error: {e}")
                flash('An error occurred. Please try again.', 'error')
    
    # Handle nickname change
    if 'change_nickname' in request.form and nickname_form.validate_on_submit():
        user_email = session.get('user_email')
        new_nickname = nickname_form.nickname.data.strip()
        
        try:
            conn = get_db_connection()
            conn.execute("UPDATE users SET nickname = ? WHERE email = ?", (new_nickname, user_email))
            conn.commit()
            conn.close()
            
            # Update session
            session['user_nickname'] = new_nickname
            flash('Nickname updated successfully!', 'success')
            logger.info(f"Nickname changed for {user_email}")
        except Exception as e:
            logger.error(f"Nickname change error: {e}")
            flash('An error occurred. Please try again.', 'error')
    
    return render_template('settings.html', password_form=password_form, nickname_form=nickname_form)


@app.route('/')
@limiter.limit("30 per minute")
def index():
    """Home page."""
    return render_template('index.html')


@app.route('/subscribe', methods=['GET', 'POST'])
@login_required
@limiter.limit("10 per minute")  # Stricter limit for submissions
def subscribe():
    """Secure subscriptions management page."""
    form = SubscribeForm()
    tab = request.args.get('tab')
    if not tab:
        tab = 'weather'
    error = None
    subscriptions = []
    # Get subscriptions for the logged-in user
    user_email = session.get('user_email')
    if user_email:
        # Weather subscription (from unified schema)
        conn = get_db_connection()
        try:
            weather_sub = conn.execute("""
                SELECT ws.email, ws.location, u.timezone, ws.personality, ws.language, ws.updated_at 
                FROM weather_subscriptions ws
                JOIN users u ON ws.email = u.email
                WHERE ws.email = ? AND u.weather_enabled = 1
            """, (user_email,)).fetchone()
            if weather_sub:
                subscriptions.append({
                    'id': f"weather_{weather_sub['email']}",
                    'type': 'weather',
                    'name': weather_sub['location'],
                    'location': weather_sub['location'],
                    'language': weather_sub['language'],
                    'personality': weather_sub['personality'],
                    'date_added': weather_sub['updated_at'],
                })
        finally:
            conn.close()
        # Countdown subscriptions
        from services.countdown_service import get_user_countdowns
        countdowns = get_user_countdowns(user_email)
        for cd in countdowns:
            subscriptions.append({
                'id': f"countdown_{cd.name}_{cd.date}",
                'type': 'countdown',
                'name': cd.name,
                'date': cd.date,
                'date_added': cd.date,
                'message_before': cd.message_before,
                'yearly': cd.yearly,
            })

    if request.method == 'POST':
        try:
            email = session.get('user_email')
            if not email:
                flash('Session expired. Please log in again.', 'error')
                return redirect(url_for('login'))
            if tab == 'weather':
                # Weather subscription form
                location = request.form.get('location', '').strip()
                language = request.form.get('language', '')
                personality = request.form.get('personality', '')
                logger.info(f"Processing weather subscription for {email} - {location}")
                geocode_result = geocode_location(location)
                if not geocode_result:
                    flash('Could not find that location. Please try a more specific address (e.g., "Bratislava, Slovakia")', 'error')
                    return render_template('subscribe.html', form=form, tab='weather', error=error)
                lat, lon, display_name, timezone_str = geocode_result
                
                # Use subscription service which handles unified schema
                from services.subscription_service import add_or_update_subscriber
                try:
                    add_or_update_subscriber(email, display_name, lat, lon, personality, language, timezone_str)
                    logger.info(f"Weather subscription added/updated for {email} in timezone {timezone_str}")
                    flash(f'✅ Successfully subscribed to daily weather for {sanitize_output(display_name)} (emails at 05:00 {timezone_str})!', 'success')
                    return redirect(url_for('subscribe', tab='subscriptions', success='weather'))
                except Exception as e:
                    logger.error(f"Subscription error: {e}")
                    flash('An error occurred. Please try again later.', 'error')
                    return render_template('subscribe.html', form=form, tab='weather', error=str(e), subscriptions=subscriptions)
            elif tab == 'countdown':
                # Countdown subscription form
                countdown_name = request.form.get('countdown_name', '').strip()
                countdown_date = request.form.get('countdown_date', '').strip()
                countdown_yearly = bool(request.form.get('countdown_yearly'))
                countdown_message_before = request.form.get('countdown_message_before', '').strip()
                countdown_message_after = request.form.get('countdown_message_after', '').strip()
                
                # Validate required fields
                if not countdown_name:
                    flash('Countdown name is required.', 'error')
                    return render_template('subscribe.html', form=form, tab='countdown', error='Name required', subscriptions=subscriptions)
                if not countdown_date:
                    flash('Countdown date is required.', 'error')
                    return render_template('subscribe.html', form=form, tab='countdown', error='Date required', subscriptions=subscriptions)
                if not countdown_message_before:
                    flash('Message before event is required.', 'error')
                    return render_template('subscribe.html', form=form, tab='countdown', error='Message required', subscriptions=subscriptions)
                
                logger.info(f"Processing countdown subscription for {email} - {countdown_name} on {countdown_date}")
                try:
                    event = CountdownEvent(
                        name=countdown_name,
                        date=countdown_date,
                        yearly=countdown_yearly,
                        email=email,
                        message_before=countdown_message_before,
                        message_after=countdown_message_after
                    )
                    add_countdown(event)
                    flash(f'✅ Successfully subscribed to countdown: {sanitize_output(countdown_name)} ({countdown_date})!', 'success')
                    return redirect(url_for('subscribe', tab='subscriptions', success='countdown'))
                except ValueError as e:
                    # Handle duplicate or validation errors
                    logger.error(f"Countdown validation error: {e}")
                    flash(f'Error: {str(e)}', 'error')
                    return render_template('subscribe.html', form=form, tab='countdown', error=str(e), subscriptions=subscriptions)
                except Exception as e:
                    logger.error(f"Countdown subscription error: {e}", exc_info=True)
                    flash(f'An error occurred while saving countdown: {str(e)}', 'error')
                    return render_template('subscribe.html', form=form, tab='countdown', error=str(e), subscriptions=subscriptions)
        except Exception as e:
            logger.error(f"Subscription error: {e}")
            flash('An unexpected error occurred. Please try again.', 'error')
    return render_template('subscribe.html', form=form, tab=tab, error=error, subscriptions=subscriptions)


@app.route('/preview')
@login_required
@limiter.limit("20 per minute")
def preview():
    """Preview weather email for a subscriber."""
    # Use logged-in user's email
    email = session.get('user_email')
    
    if not email:
        flash('Session expired. Please log in again.', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    try:
        # Parameterized query (SQL injection safe) - unified schema
        subscriber = conn.execute("""
            SELECT ws.email, ws.location, ws.lat, ws.lon, 
                   COALESCE(u.timezone, 'UTC') as timezone, 
                   ws.personality, ws.language 
            FROM weather_subscriptions ws
            JOIN users u ON ws.email = u.email
            WHERE ws.email = ?
        """, (email,)).fetchone()
        
        if not subscriber:
            flash('No weather subscription found. Please subscribe first.', 'info')
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
        # Get aggregate statistics from unified schema
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

@app.route('/api/update_subscription', methods=['POST'])
@limiter.limit("20 per minute")
@csrf.exempt  # For API calls, but we still validate
def api_update_subscription():
    """API to update a subscription (weather or countdown) from modal edit form."""
    try:
        data = request.get_json()
        if not data or 'id' not in data:
            return jsonify({'status': 'error', 'message': 'Missing subscription ID'}), 400

        sub_id = data['id']
        # Weather subscription: id starts with 'weather_'
        if sub_id.startswith('weather_'):
            email = sub_id.replace('weather_', '', 1)
            location = data.get('location', '').strip()
            language = data.get('language', '')
            personality = data.get('personality', '')
            
            try:
                # Geocode location if changed
                from services.weather_service import geocode_location
                geocode_result = geocode_location(location)
                if not geocode_result:
                    return jsonify({'status': 'error', 'message': 'Invalid location'}), 400
                
                lat, lon, display_name, timezone_str = geocode_result
                
                # Use subscription service to update (handles unified schema)
                from services.subscription_service import add_or_update_subscriber
                add_or_update_subscriber(email, display_name, lat, lon, personality, language, timezone_str)
                
                return jsonify({'status': 'success'})
            except Exception as e:
                logger.error(f"Weather update error: {e}")
                return jsonify({'status': 'error', 'message': str(e)}), 500
        # Countdown subscription: id starts with 'countdown_'
        elif sub_id.startswith('countdown_'):
            # id format: countdown_{name}_{date}
            parts = sub_id.split('_', 2)
            if len(parts) < 3:
                return jsonify({'status': 'error', 'message': 'Invalid countdown ID'}), 400
            name = parts[1]
            date = parts[2]
            # Get fields
            new_name = data.get('name', name)
            new_date = data.get('date', date)
            yearly = bool(data.get('yearly', False))
            message_before = data.get('message_before', '')
            # Update countdown in DB
            conn = get_db_connection()
            try:
                # Find countdown by name and date
                cursor = conn.execute("""
                    SELECT * FROM countdowns WHERE name = ? AND date = ?
                """, (name, date))
                countdown = cursor.fetchone()
                if not countdown:
                    return jsonify({'status': 'error', 'message': 'Countdown not found'}), 404
                conn.execute("""
                    UPDATE countdowns SET name = ?, date = ?, yearly = ?, message_before = ?
                    WHERE name = ? AND date = ?
                """, (new_name, new_date, int(yearly), message_before, name, date))
                conn.commit()
                return jsonify({'status': 'success'})
            except Exception as e:
                logger.error(f"Countdown update error: {e}")
                return jsonify({'status': 'error', 'message': str(e)}), 500
            finally:
                conn.close()
        else:
            return jsonify({'status': 'error', 'message': 'Unknown subscription type'}), 400
    except Exception as e:
        logger.error(f"API update error: {e}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500
    
    
# --- API endpoint to delete a subscription ---
@app.route('/api/delete_subscription', methods=['POST'])
@limiter.limit("20 per minute")
@csrf.exempt
def api_delete_subscription():
    """API to delete a subscription (weather or countdown) from modal or card."""
    try:
        data = request.get_json()
        if not data or 'id' not in data:
            return jsonify({'status': 'error', 'message': 'Missing subscription ID'}), 400

        sub_id = data['id']
        if sub_id.startswith('weather_'):
            email = sub_id.replace('weather_', '', 1)
            try:
                from services.subscription_service import delete_subscriber
                deleted = delete_subscriber(email)
                if deleted > 0:
                    return jsonify({'status': 'success'})
                else:
                    return jsonify({'status': 'error', 'message': 'Subscription not found'}), 404
            except Exception as e:
                logger.error(f"Weather delete error: {e}")
                return jsonify({'status': 'error', 'message': str(e)}), 500
        elif sub_id.startswith('countdown_'):
            parts = sub_id.split('_', 2)
            if len(parts) < 3:
                return jsonify({'status': 'error', 'message': 'Invalid countdown ID'}), 400
            name = parts[1]
            date = parts[2]
            conn = get_db_connection()
            try:
                cursor = conn.execute('DELETE FROM countdowns WHERE name = ? AND date = ?', (name, date))
                conn.commit()
                if cursor.rowcount > 0:
                    return jsonify({'status': 'success'})
                else:
                    return jsonify({'status': 'error', 'message': 'Countdown not found'}), 404
            except Exception as e:
                logger.error(f"Countdown delete error: {e}")
                return jsonify({'status': 'error', 'message': str(e)}), 500
            finally:
                conn.close()
        else:
            return jsonify({'status': 'error', 'message': 'Unknown subscription type'}), 400
    except Exception as e:
        logger.error(f"API delete error: {e}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


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
            subscriber = conn.execute("""
                SELECT ws.email, ws.location, ws.personality, ws.language 
                FROM weather_subscriptions ws
                JOIN users u ON ws.email = u.email
                WHERE ws.email = ? AND u.weather_enabled = 1
            """, (email,)).fetchone()
            
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
