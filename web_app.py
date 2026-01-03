# --- All imports at the top, deduplicated and complete ---
import os
import sys
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
from api_client import get_api_client
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

# Initialize API client
try:
    api_client = get_api_client()
    logger.info(f"✅ API client initialized: {api_client.base_url}")
except Exception as e:
    logger.error(f"Failed to initialize API client: {e}")
    api_client = None


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
        
        success, message = api_client.register_user(
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
        
        user = api_client.authenticate_user(email, password)
        if user:
            session['user_email'] = user['email']
            session['user_nickname'] = user.get('nickname')
            session['user_username'] = user.get('username')
            session.permanent = False  # Session expires when browser closes
            return jsonify({'success': True, 'message': 'Login successful'})
        else:
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
    
    # Handle regular form submission
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data
        
        user = api_client.authenticate_user(email, password)
        if user:
            session['user_email'] = user['email']
            session['user_nickname'] = user.get('nickname')
            session['user_username'] = user.get('username')
            session.permanent = False
            flash('Login successful!', 'success')
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html', form=form)


@app.route('/forgot-password', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def forgot_password():
    """Forgot password page."""
    if 'user_email' in session:
        flash('You are already logged in.', 'info')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        if not email:
            flash('Please enter your email address', 'error')
            return render_template('forgot_password.html')
        
        success, message = api_client.request_password_reset(email)
        if success:
            flash('Password reset link has been sent to your email!', 'success')
            return redirect(url_for('login'))
        else:
            flash(f'{message}', 'error')
            return render_template('forgot_password.html')
    
    return render_template('forgot_password.html')


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def reset_password(token):
    """Reset password with token."""
    if 'user_email' in session:
        flash('You are already logged in.', 'info')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not new_password or not confirm_password:
            flash('Please fill in all fields', 'error')
            return render_template('reset_password.html', token=token)
        
        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('reset_password.html', token=token)
        
        if len(new_password) < 8:
            flash('Password must be at least 8 characters long', 'error')
            return render_template('reset_password.html', token=token)
        
        success, message = api_client.reset_password(token, new_password)
        if success:
            flash('Password reset successful! Please log in with your new password.', 'success')
            return redirect(url_for('login'))
        else:
            flash(f'Error: {message}', 'error')
            return render_template('reset_password.html', token=token)
    
    return render_template('reset_password.html', token=token)


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
        user = api_client.authenticate_user(user_email, current_password)
        if not user:
            flash('Current password is incorrect.', 'error')
        else:
            # Update password
            if api_client.update_password(user_email, new_password):
                flash('Password updated successfully!', 'success')
                logger.info(f"Password changed for {user_email}")
            else:
                flash('An error occurred. Please try again.', 'error')
    
    # Handle nickname change
    if 'change_nickname' in request.form and nickname_form.validate_on_submit():
        user_email = session.get('user_email')
        new_nickname = nickname_form.nickname.data.strip()
        
        if api_client.update_nickname(user_email, new_nickname):
            # Update session
            session['user_nickname'] = new_nickname
            flash('Nickname updated successfully!', 'success')
            logger.info(f"Nickname changed for {user_email}")
        else:
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
        # Weather subscription
        weather_sub = api_client.get_weather_subscription(user_email)
        if weather_sub:
            subscriptions.append({
                'id': f"weather_{weather_sub['email']}",
                'type': 'weather',
                'name': weather_sub['location'],
                'location': weather_sub['location'],
                'language': weather_sub.get('language', 'en'),
                'personality': weather_sub.get('personality', 'neutral'),
                'date_added': weather_sub.get('timezone', 'UTC'),
            })
        
        # Countdown subscriptions
        countdowns = api_client.get_countdowns(user_email)
        for cd in countdowns:
            subscriptions.append({
                'id': f"countdown_{cd['id']}",
                'type': 'countdown',
                'name': cd['name'],
                'date': cd['date'],
                'date_added': cd.get('created_at', cd['date']),
                'message_before': cd.get('message_before', ''),
                'yearly': cd.get('yearly', False),
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
                
                success, result = api_client.create_weather_subscription(
                    email=email,
                    location=location,
                    personality=personality,
                    language=language
                )
                
                if success:
                    logger.info(f"Weather subscription added/updated for {email}")
                    flash(f'✅ Successfully subscribed to daily weather for {sanitize_output(result)}!', 'success')
                    return redirect(url_for('subscribe', tab='subscriptions', success='weather'))
                else:
                    flash(f'Could not subscribe: {result}', 'error')
                    return render_template('subscribe.html', form=form, tab='weather', error=result, subscriptions=subscriptions)
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
                
                if api_client.create_countdown(
                    email=email,
                    name=countdown_name,
                    date=countdown_date,
                    yearly=countdown_yearly,
                    message_before=countdown_message_before,
                    message_after=countdown_message_after
                ):
                    flash(f'✅ Successfully subscribed to countdown: {sanitize_output(countdown_name)} ({countdown_date})!', 'success')
                    return redirect(url_for('subscribe', tab='subscriptions', success='countdown'))
                else:
                    flash('Error creating countdown', 'error')
                    return render_template('subscribe.html', form=form, tab='countdown', error='Failed to create', subscriptions=subscriptions)
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
    
    try:
        # Get weather preview from API
        preview_data = api_client.preview_weather(email)
        
        if not preview_data:
            flash('No weather subscription found. Please subscribe first.', 'info')
            return redirect(url_for('subscribe'))
        
        return render_template('preview.html', 
                             subscriber=preview_data['subscriber'],
                             weather_summary=preview_data['weather_summary'])
    
    except Exception as e:
        logger.error(f"Preview error: {e}")
        flash('An error occurred loading the preview', 'error')
        return redirect(url_for('index'))


@app.route('/stats')
@limiter.limit("20 per minute")
def stats():
    """Public statistics page (no sensitive data)."""
    try:
        stats_data = api_client.get_stats()
        if stats_data:
            return render_template('stats.html',
                                 total=stats_data['total'],
                                 languages=stats_data['languages'],
                                 personalities=stats_data['personalities'])
        else:
            flash('Unable to load statistics', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Stats error: {e}")
        flash('Unable to load statistics', 'error')
        return redirect(url_for('index'))


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
                success, result = api_client.create_weather_subscription(
                    email=email,
                    location=location,
                    personality=personality,
                    language=language
                )
                
                if success:
                    return jsonify({'status': 'success'})
                else:
                    return jsonify({'status': 'error', 'message': result}), 400
            except Exception as e:
                logger.error(f"Weather update error: {e}")
                return jsonify({'status': 'error', 'message': str(e)}), 500
        # Countdown subscription: id starts with 'countdown_'
        elif sub_id.startswith('countdown_'):
            # id format: countdown_{id}
            parts = sub_id.split('_', 1)
            if len(parts) < 2:
                return jsonify({'status': 'error', 'message': 'Invalid countdown ID'}), 400
            
            countdown_id = int(parts[1])
            new_name = data.get('name', '')
            new_date = data.get('date', '')
            yearly = bool(data.get('yearly', False))
            message_before = data.get('message_before', '')
            
            try:
                if api_client.update_countdown(countdown_id, new_name, new_date, yearly, message_before):
                    return jsonify({'status': 'success'})
                else:
                    return jsonify({'status': 'error', 'message': 'Countdown not found'}), 404
            except Exception as e:
                logger.error(f"Countdown update error: {e}")
                return jsonify({'status': 'error', 'message': str(e)}), 500
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
                if api_client.delete_weather_subscription(email):
                    return jsonify({'status': 'success'})
                else:
                    return jsonify({'status': 'error', 'message': 'Subscription not found'}), 404
            except Exception as e:
                logger.error(f"Weather delete error: {e}")
                return jsonify({'status': 'error', 'message': str(e)}), 500
        elif sub_id.startswith('countdown_'):
            parts = sub_id.split('_', 1)
            if len(parts) < 2:
                return jsonify({'status': 'error', 'message': 'Invalid countdown ID'}), 400
            
            countdown_id = int(parts[1])
            try:
                if api_client.delete_countdown(countdown_id):
                    return jsonify({'status': 'success'})
                else:
                    return jsonify({'status': 'error', 'message': 'Countdown not found'}), 404
            except Exception as e:
                logger.error(f"Countdown delete error: {e}")
                return jsonify({'status': 'error', 'message': str(e)}), 500
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
        
        subscriber = api_client.get_weather_subscription(email)
        if subscriber:
            return jsonify({
                'subscribed': True,
                'location': subscriber.get('location', ''),
                'personality': subscriber.get('personality', 'neutral'),
                'language': subscriber.get('language', 'en')
            })
        else:
            return jsonify({'subscribed': False})
    
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
