#!/usr/bin/env python3
"""Send immediate test email with nameday feature to specified user"""

import sys
import os
from datetime import datetime

# Add project root to sys.path for module imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import Config, load_env
from services.weather_service import get_weather_forecast, geocode_location, generate_daily_summary
from services.email_service import send_email

def send_test_nameday_email(target_email, location="Bratislava", language="sk", personality="neutral"):
    """Send a test email with weather and nameday to the specified user."""
    
    print(f"📧 Preparing to send test email to: {target_email}")
    print("=" * 50)
    
    # Load configuration
    try:
        config = load_env()
        print(f"✅ Configuration loaded - From: {config.email_address}")
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return False
    
    print(f"📍 Location: {location}")
    print(f"🎭 Personality: {personality}")
    print(f"🌍 Language: {language}")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
    
    # Geocode location
    print("🗺️ Geocoding location...")
    coords = geocode_location(location)
    if not coords:
        print(f"❌ Failed to geocode location: {location}")
        return False
    
    lat, lon, display_name = coords
    print(f"✅ Geocoded to: {lat}, {lon}")
    
    # Get weather forecast
    print("🌤️ Fetching weather forecast...")
    weather = get_weather_forecast(lat, lon, config.timezone)
    
    if not weather:
        print("❌ Failed to get weather data")
        return False
    
    print(f"✅ Weather data retrieved")
    
    # Generate daily summary (includes weather + nameday)
    print("📝 Generating daily summary with nameday...")
    message = generate_daily_summary(
        weather=weather,
        location=location,
        personality=personality,
        language=language,
        countdowns=None,
        reminders=None
    )
    
    if not message:
        print("❌ Failed to generate message")
        return False
    
    print(f"✅ Message generated ({len(message)} characters)")
    print("\n📝 Message preview:")
    print("-" * 50)
    print(message)
    print("-" * 50)
    
    # Send email
    print("\n📤 Sending email...")
    subject = "🌤️ Daily Weather & Name Day - Test Message"
    
    try:
        success = send_email(config, target_email, subject, message, dry_run=False)
        
        if success:
            print("✅ Email sent successfully!")
            print(f"📧 Sent to: {target_email}")
            print(f"📄 Subject: {subject}")
            return True
        else:
            print("❌ Failed to send email")
            return False
            
    except Exception as e:
        print(f"❌ Email sending error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Daily Brief Service - Test Email with Name Day")
    print()
    
    # Configuration
    target = "filip.johanes9@gmail.com"
    location = "Bratislava"
    language = "sk"  # Slovak - supports namedays
    personality = "neutral"
    
    print(f"🎯 Target: {target}")
    print(f"📍 Location: {location}")
    print(f"🌍 Language: {language}")
    print()
    
    success = send_test_nameday_email(target, location, language, personality)
    
    if success:
        print("\n🎉 Test email sent successfully!")
        print("📱 Check your inbox for the weather forecast with name day!")
    else:
        print("\n❌ Failed to send test email")
        print("🔧 Check configuration and network connection")
