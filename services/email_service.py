# --- Daily Job Handler ---
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

        
def run_daily_job(config, dry_run=False, db_path="app.db"):
    """Send daily emails to all subscribers (weather, countdowns, etc)."""
    logger.info("Running daily job - sending emails every 5 minutes for testing")
    conn = sqlite3.connect(db_path)
    try:
        # Select all active users, join with weather table for location and coordinates
        users = conn.execute("""
            SELECT u.email, w.location, w.lat, w.lon, 
                   COALESCE(u.timezone, w.timezone, 'UTC') as timezone,
                   COALESCE(u.personality, w.personality, 'neutral') as personality,
                   COALESCE(u.language, w.language, 'en') as language,
                   u.weather_enabled, u.countdown_enabled, u.reminder_enabled
            FROM users u
            LEFT JOIN weather w ON u.email = w.email
            WHERE u.active=1
        """).fetchall()
        logger.info(f"Checking {len(users)} users for test delivery")
        sent_count = 0
        for email_addr, location, lat, lon, user_tz, personality, language, weather_enabled, countdown_enabled, reminder_enabled in users:
            try:
                user_now = datetime.now(ZoneInfo(user_tz))
                # Only send if it's 5AM in user's local time
                if user_now.hour != 5:
                    continue
                email_body = ""
                # Weather section
                if weather_enabled and location and lat is not None and lon is not None:
                    weather = get_weather_forecast(lat, lon, user_tz)
                    if weather:
                        email_body += generate_weather_summary(weather, location, personality, language) + "\n\n"
                    else:
                        logger.warning(f"No weather data for {email_addr} at {location}")
                # Countdown section
                if countdown_enabled:
                    email_body += generate_countdown_summary(email_addr, user_now, user_tz) + "\n"
                # Reminder section
                if reminder_enabled:
                    # You may want to fetch reminders from the reminders table and format them here
                    # For now, just add a placeholder
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
                        'lat': lat,
                        'lon': lon,
                        'personality': personality,
                        'language': language,
                        'timezone': user_tz,
                        'weather_enabled': bool(weather_enabled),
                        'countdown_enabled': bool(countdown_enabled),
                        'reminder_enabled': bool(reminder_enabled),
                        'weather_data': weather if weather_enabled else None,
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

