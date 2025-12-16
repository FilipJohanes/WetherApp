# --- Daily Job Handler ---
import os
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo
from services.weather_service import generate_weather_summary, get_weather_forecast
from services.countdown_service import generate_countdown_summary, get_user_countdowns
from services.logging_service import logger
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import reprlib

# Stubs for app.py imports
def start_email_monitor():
    pass

def stop_email_monitor():
    pass

def send_test_email(config, to):
    print(f"Test email sent to {to}")

# Dummy send_email for demonstration
# Replace with actual implementation

def send_email(config, to, subject, body):
    print(f"[EMAIL ATTEMPT] To: {to} | Subject: {subject}")
    print(f"[DEBUG] Using EMAIL_PASSWORD: {reprlib.repr(config.email_password)} (length: {len(config.email_password)})")
    try:
        msg = MIMEMultipart()
        msg['From'] = config.email_address
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        print(f"[DEBUG] Connecting to SMTP server: {config.smtp_host}:{config.smtp_port}")
        server = smtplib.SMTP(config.smtp_host, config.smtp_port)
        if config.smtp_use_tls:
            server.starttls()
        server.login(config.email_address, config.email_password)
        server.sendmail(config.email_address, to, msg.as_string())
        server.quit()
        print(f"[EMAIL SUCCESS] To: {to} | Subject: {subject}")
        return True
    except Exception as e:
        print(f"[EMAIL FAILURE] To: {to} | Subject: {subject} | Error: {e}")
        return False

# Example user dict: {'email': ..., 'weather_enabled': True, 'countdown_enabled': True, ...}
def send_daily_email(config, user):
    email = user['email']
    subject = "Your Daily Brief"
    body = ""
    # Weather
    if user.get('weather_enabled'):
        # You'd fetch location, personality, language, etc. from user
        location = user.get('location', 'Bratislava')
        personality = user.get('personality', 'neutral')
        language = user.get('language', 'en')
        weather = user.get('weather_data')  # Should be fetched from weather_service
        if weather:
            body += generate_weather_summary(weather, location, personality, language) + "\n\n"
    # Countdown
    print(f"[DEBUG] Fetching countdowns for {email}")
    if user.get('countdown_enabled'):
        body += generate_countdown_summary(email, datetime.now(ZoneInfo(config.timezone)), config.timezone) + "\n"
    if not body.strip():
        body = "No active subscriptions."
    result = send_email(config, email, subject, body)
    if result:
        print(f"✅ Sent daily email to {email}")
    else:
        print(f"❌ Failed to send daily email to {email}")

        
def run_daily_job(config, dry_run=False, db_path=None):
    """Send daily emails to all subscribers using unified database schema."""
    if db_path is None:
        db_path = os.getenv("APP_DB_PATH", "app.db")
    logger.info("Running daily job - checking users for delivery")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        # Select all users with any enabled module, joining with weather subscriptions
        users = conn.execute("""
            SELECT 
                u.email, 
                u.lat, 
                u.lon, 
                u.timezone,
                u.weather_enabled, 
                u.countdown_enabled, 
                u.reminder_enabled,
                ws.location,
                ws.personality,
                ws.language
            FROM users u
            LEFT JOIN weather_subscriptions ws ON u.email = ws.email
            WHERE (u.weather_enabled = 1 OR u.countdown_enabled = 1 OR u.reminder_enabled = 1)
        """).fetchall()
        
        logger.info(f"Checking {len(users)} users for delivery")
        sent_count = 0
        
        for user in users:
            email_addr = user['email']
            user_tz = user['timezone'] or 'UTC'
            
            try:
                user_now = datetime.now(ZoneInfo(user_tz))
                # Only send if it's 5AM in user's local time
                if user_now.hour != 5:
                    continue
                
                email_body = ""
                personality = user['personality'] or 'neutral'
                language = user['language'] or 'en'
                location = user['location']
                
                # Weather section
                if user['weather_enabled'] and location and user['lat'] is not None and user['lon'] is not None:
                    weather = get_weather_forecast(user['lat'], user['lon'], user_tz)
                    if weather:
                        email_body += generate_weather_summary(weather, location, personality, language) + "\n\n"
                    else:
                        logger.warning(f"No weather data for {email_addr} at {location}")
                
                # Countdown section
                if user['countdown_enabled']:
                    email_body += generate_countdown_summary(email_addr, user_now, user_tz) + "\n"
                
                # Reminder section
                if user['reminder_enabled']:
                    # TODO: Implement reminder fetching and formatting
                    email_body += "[Reminders go here]\n"
                
                if not email_body.strip():
                    email_body = "No active subscriptions."
                
                subject = f"Your Daily Brief"
                footer = f"\n\n---\nDaily Brief Service ({personality} mode, {language})\nTo unsubscribe, reply with 'delete'"
                full_message = email_body + footer
                
                if dry_run:
                    print(f"[DRY RUN] Would send daily email to {email_addr} at {user_now.strftime('%H:%M')} {user_tz}")
                else:
                    send_daily_email(config, {
                        'email': email_addr,
                        'location': location,
                        'lat': user['lat'],
                        'lon': user['lon'],
                        'personality': personality,
                        'language': language,
                        'timezone': user_tz,
                        'weather_enabled': bool(user['weather_enabled']),
                        'countdown_enabled': bool(user['countdown_enabled']),
                        'reminder_enabled': bool(user['reminder_enabled']),
                        'weather_data': None,  # Already included in body
                        'email_body': full_message,
                    })
                    sent_count += 1
                    logger.info(f"✅ Sent daily brief to {email_addr} ({sent_count} total)")
            except Exception as e:
                logger.error(f"Error processing user {email_addr}: {e}")
        
        if sent_count > 0:
            logger.info(f"✅ Daily job complete - sent {sent_count} emails")
        else:
            logger.info("No emails sent this run")
    finally:
        conn.close()

