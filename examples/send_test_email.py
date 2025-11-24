#!/usr/bin/env python3
"""Send immediate test weather email to specified user"""

import sys
import os
# Add project root to sys.path for module imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import Config, load_env
from services.weather_service import get_weather_forecast, geocode_location, generate_weather_summary
from services.email_service import send_email
import sqlite3

def send_test_weather_email(target_email):
    """Send a test weather email to the specified user."""
    
    print(f"📧 Preparing to send test weather email to: {target_email}")
    print("=" * 50)
    
    # Load configuration
    try:
        config = load_env()
        print(f"✅ Configuration loaded - From: {config.email_address}")
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return False
    
    # Get user details from database
    conn = sqlite3.connect("examples/app.db")
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT email, location, lat, lon, personality, language 
            FROM users 
            WHERE email = ?
        """, (target_email,))
        
        user_data = cursor.fetchone()
        
        if not user_data:
            print(f"❌ User {target_email} not found in database!")
            return False
        
        email, location, lat, lon, personality, language = user_data
        print(f"📍 Location: {location} ({lat}, {lon})")
        print(f"🎭 Personality: {personality}")
        print(f"🌍 Language: {language}")
        
    finally:
        conn.close()
    
    # Check if we have coordinates
    if lat is None or lon is None:
        print("🗺️ Missing coordinates, attempting to geocode...")
        coords = geocode_location(location)
        if coords:
            lat, lon, display_name = coords
            print(f"✅ Geocoded to: {lat}, {lon}")
        else:
            print(f"❌ Failed to geocode location: {location}")
            return False
    
    # Get weather forecast
    print("🌤️ Fetching weather forecast...")
    weather = get_weather_forecast(lat, lon, config.timezone)
    
    if not weather:
        print("❌ Failed to get weather data")
        return False
    
    print(f"✅ Weather data retrieved - Current: {weather.get('current_temperature', 'N/A')}°C")
    
    # Generate weather message
    print("📝 Generating weather message...")
    message = generate_weather_summary(weather, location, personality, language)
    
    if not message:
        print("❌ Failed to generate weather message")
        return False
    
    print(f"✅ Message generated ({len(message)} characters)")
    
    # Send email
    print("📤 Sending email...")
    subject = "🌤️ Daily Weather Forecast - Test Message"
    
    try:
        success = send_email(config, target_email, subject, message, dry_run=False)
        
        if success:
            print("✅ Email sent successfully!")
            print(f"📧 Sent to: {target_email}")
            print(f"📄 Subject: {subject}")
            print("\n📝 Message preview:")
            print("-" * 30)
            print(message[:200] + "..." if len(message) > 200 else message)
            print("-" * 30)
            return True
        else:
            print("❌ Failed to send email")
            return False
            
    except Exception as e:
        print(f"❌ Email sending error: {e}")
        return False

if __name__ == "__main__":
    # Send to Filip's email
    target = "filip.johanes9@gmail.com"
    
    print("🧪 Daily Brief Service - Test Email Sender")
    print(f"🎯 Target: {target}")
    print()
    
    success = send_test_weather_email(target)
    
    if success:
        print("\n🎉 Test email sent successfully!")
        print("📱 Check your inbox for the weather forecast!")
    else:
        print("\n❌ Failed to send test email")
        print("🔧 Check configuration and network connection")