#!/usr/bin/env python3
"""
Updated weather email sender using the new localization system
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import Config, load_env, get_weather_forecast, send_email
from localization import get_localized_message, get_localized_subject
import sqlite3

def determine_weather_condition(weather_data):
    """Determine weather condition from API data for message selection."""
    
    temp_max = weather_data.get('temp_max', 20)
    temp_min = weather_data.get('temp_min', 10)
    precipitation = weather_data.get('precipitation_sum', 0)
    wind_speed = weather_data.get('wind_speed_max', 0)
    
    # Simple weather condition logic
    if precipitation > 5:
        return 'rainy'
    elif temp_max > 30:
        return 'hot'
    elif temp_max < 5:
        return 'cold'
    elif wind_speed > 20:
        return 'windy'
    elif 15 <= temp_max <= 25:
        return 'mild'
    else:
        return 'sunny'  # Default

def generate_localized_weather_message(weather, location, personality="neutral", language="en"):
    """Generate a complete localized weather message."""
    
    # Determine weather condition
    condition = determine_weather_condition(weather)
    
    # Get localized weather condition message
    condition_message = get_localized_message(condition, personality, language)
    
    # Get weather data
    temp_max = weather.get('temp_max', 'N/A')
    temp_min = weather.get('temp_min', 'N/A')
    precipitation = weather.get('precipitation_sum', 0)
    wind_speed = weather.get('wind_speed_max', 'N/A')
    
    # Build complete message with weather data
    if language == 'en':
        weather_data = f"""📊 Today's Details:
• High: {temp_max}°C
• Low: {temp_min}°C  
• Precipitation: {precipitation}mm
• Wind: {wind_speed} km/h

{condition_message}

---
Daily Brief Service | Unsubscribe: Reply "delete" """
    
    elif language == 'es':
        weather_data = f"""📊 Detalles de Hoy:
• Máxima: {temp_max}°C
• Mínima: {temp_min}°C  
• Precipitación: {precipitation}mm
• Viento: {wind_speed} km/h

{condition_message}

---
Servicio Daily Brief | Cancelar: Responde "delete" """
    
    elif language == 'sk':
        weather_data = f"""📊 Dnešné údaje:
• Maximum: {temp_max}°C
• Minimum: {temp_min}°C  
• Zrážky: {precipitation}mm
• Vietor: {wind_speed} km/h

{condition_message}

---
Služba Daily Brief | Zrušiť: Odpíš "delete" """
    
    return weather_data

def send_localized_weather_email(target_email):
    """Send properly localized weather email."""
    
    print(f"📧 Sending localized weather email to: {target_email}")
    
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
    
    # Generate localized message
    print(f"📝 Generating {language} message with {personality} personality...")
    message = generate_localized_weather_message(weather, location, personality, language)
    
    # Get localized subject
    subject = get_localized_subject('daily_forecast_subject', personality, language, location=location)
    
    # Send email
    print("📤 Sending...")
    
    try:
        success = send_email(config, target_email, subject, message, dry_run=False)
        
        if success:
            print("✅ LOCALIZED EMAIL SENT!")
            print(f"\n📧 Subject: {subject}")
            print("\n📝 Message sent:")
            print("=" * 50)
            print(message)
            print("=" * 50)
            return True
        else:
            print("❌ Send failed")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    # Only send to your email - not bothering other people!
    success = send_localized_weather_email("filip.johanes9@gmail.com")
    
    if success:
        print("\n🎉 Check your email inbox for the fully localized weather report!")
        print("📧 Only sent to filip.johanes9@gmail.com - no spam!")
    else:
        print("\n❌ Failed to send localized email")