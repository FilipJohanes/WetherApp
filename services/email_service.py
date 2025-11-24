import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo
from services.summary_service import generate_weather_summary
from services.countdown_service import generate_countdown_summary, get_user_countdowns
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
        print("[DEBUG] Connection established.")
        if config.smtp_use_tls:
            print("[DEBUG] Starting TLS...")
            server.starttls()
            print("[DEBUG] TLS started.")
        print(f"[DEBUG] Logging in as {config.email_address}")
        server.login(config.email_address, config.email_password)
        print("[DEBUG] Login successful.")
        print("[DEBUG] Sending email...")
        server.sendmail(config.email_address, to, msg.as_string())
        print("[DEBUG] Email sent.")
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
    print("COUNTDOWN User dict:", user)
    if user.get('countdown_enabled'):
        body += generate_countdown_summary(email, datetime.now(ZoneInfo(config.timezone)), config.timezone) + "\n"
    else:
        body += "countdown error\n"
    if not body.strip():
        body = "No active subscriptions."
    result = send_email(config, email, subject, body)
    if result:
        print(f"✅ Sent daily email to {email}")
    else:
        print(f"❌ Failed to send daily email to {email}")

