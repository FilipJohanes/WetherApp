# email_service.py
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo
from services.weather_service import generate_weather_summary
from services.countdown_service import generate_countdown_summary, get_user_countdowns

# Dummy send_email for demonstration
# Replace with actual implementation

def send_email(config, to, subject, body):
    print(f"Sending email to {to}: {subject}\n{body}")

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
    if user.get('countdown_enabled'):
        body += generate_countdown_summary(email, datetime.now(ZoneInfo(config.timezone)), config.timezone) + "\n"
    if not body.strip():
        body = "No active subscriptions."
    send_email(config, email, subject, body)

