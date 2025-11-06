#!/usr/bin/env python3
"""Send immediate weather email with working message generation"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import Config, load_env, get_weather_forecast, send_email
import sqlite3

def generate_simple_weather_message(weather, location, personality="brutal", language="en"):
    """Generate a simple weather message that works with current data."""
    
    temp_max = weather.get('temp_max', 'N/A')
    temp_min = weather.get('temp_min', 'N/A')
    precipitation = weather.get('precipitation_sum', 0)
    wind_speed = weather.get('wind_speed_max', 'N/A')
    
    if personality == "brutal":
        if language == "en":
            message = f"""🌤️ WEATHER REPORT - {location.upper()}

TODAY'S FORECAST (No-nonsense edition):
• High: {temp_max}°C
• Low: {temp_min}°C  
• Rain: {precipitation}mm
• Wind: {wind_speed} km/h

That's it. Check the weather. Dress accordingly. 
Don't complain if you get wet.

--
Daily Brief Service
Unsubscribe: Reply with "delete"
"""
        else:
            message = f"""🌤️ POČASIE - {location.upper()}

DNEŠNÁ PREDPOVEĎ:
• Maximum: {temp_max}°C
• Minimum: {temp_min}°C
• Zrážky: {precipitation}mm  
• Vietor: {wind_speed} km/h

To je všetko. Pozri si počasie. Obleč sa podľa toho.

--
Daily Brief Service
Odhlásenie: Odpíš "delete" 
"""
    else:
        # Default neutral
        message = f"""🌤️ Daily Weather - {location}

Today's forecast:
• High temperature: {temp_max}°C
• Low temperature: {temp_min}°C
• Precipitation: {precipitation}mm
• Wind speed: {wind_speed} km/h

Have a great day!

--
Daily Brief Service
"""
    
    return message

def send_immediate_weather_email(target_email):
    """Send weather email right now."""
    
    print(f"📧 Sending immediate weather email to: {target_email}")
    
    # Load config
    config = load_env()
    
    # Get user from database
    conn = sqlite3.connect("app.db")
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT email, location, lat, lon, personality, language 
            FROM subscribers WHERE email = ?
        """, (target_email,))
        
        user_data = cursor.fetchone()
        if not user_data:
            print(f"❌ User {target_email} not found!")
            return False
            
        email, location, lat, lon, personality, language = user_data
        print(f"📍 {location} | 🎭 {personality} | 🌍 {language}")
        
    finally:
        conn.close()
    
    # Get weather
    print("🌤️ Getting weather...")
    weather = get_weather_forecast(lat, lon, config.timezone)
    
    if not weather:
        print("❌ No weather data")
        return False
    
    # Generate message
    message = generate_simple_weather_message(weather, location, personality, language)
    
    # Send email
    print("📤 Sending...")
    subject = "🌤️ Daily Weather Forecast - Immediate Test"
    
    try:
        success = send_email(config, target_email, subject, message, dry_run=False)
        
        if success:
            print("✅ EMAIL SENT!")
            print("\n📝 Message sent:")
            print("=" * 40)
            print(message)
            print("=" * 40)
            return True
        else:
            print("❌ Send failed")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = send_immediate_weather_email("filip.johanes9@gmail.com")
    
    if success:
        print("\n🎉 Check your email inbox!")
    else:
        print("\n❌ Failed to send email")