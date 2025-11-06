#!/usr/bin/env python3
"""
Hybrid localization system that uses:
1. Existing weather_messages.txt for weather conditions (keeping your emuska messages!)
2. New localization system for system messages (subjects, headers, footers)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # Go up one level

from app import Config, load_env, get_weather_forecast, send_email, load_weather_messages
from localization import get_localized_subject
import sqlite3

def determine_weather_condition(weather_data):
    """Determine weather condition from API data."""
    
    temp_max = weather_data.get('temp_max', 20)
    temp_min = weather_data.get('temp_min', 10)
    precipitation = weather_data.get('precipitation_sum', 0)
    wind_speed = weather_data.get('wind_speed_max', 0)
    
    # Enhanced weather condition logic to match your weather_messages.txt
    if precipitation > 10:
        return 'heavy_rain'
    elif precipitation > 2:
        return 'raining'
    elif temp_max > 35:
        return 'heatwave'
    elif temp_max > 28:
        if precipitation > 0:
            return 'sunny_hot'
        return 'hot'
    elif temp_max < 0:
        if precipitation > 0:
            return 'blizzard'
        return 'freezing'
    elif temp_max < 5:
        if wind_speed > 20:
            return 'cold_windy'
        elif precipitation > 0:
            return 'rainy_cold'
        return 'cold'
    elif wind_speed > 25:
        return 'windy'
    elif temp_max >= 15 and temp_max <= 25:
        return 'mild'
    elif precipitation == 0 and temp_max > 20:
        return 'sunny'
    else:
        return 'cloudy'

def get_weather_condition_message(condition, personality, language):
    """Get weather condition message from weather_messages.txt files."""
    
    # Load the actual weather messages from your files
    weather_messages = load_weather_messages(language)
    
    if condition in weather_messages:
        message_variants = weather_messages[condition]
        
        # Get the specific personality message
        if personality in message_variants:
            return message_variants[personality]
        elif personality == 'emuska' and language != 'sk':
            # Fallback for emuska in non-Slovak languages
            return message_variants.get('cute', message_variants.get('neutral', ''))
        else:
            return message_variants.get('neutral', '')
    
    # Fallback to default message
    default_messages = weather_messages.get('default', {})
    return default_messages.get(personality, default_messages.get('neutral', 'Have a great day!'))

def generate_complete_weather_email(weather, location, personality="neutral", language="en"):
    """Generate complete weather email using both systems."""
    
    # Determine weather condition
    condition = determine_weather_condition(weather)
    
    # Get the REAL weather condition message from your weather_messages.txt
    condition_message = get_weather_condition_message(condition, personality, language)
    
    # Get weather data
    temp_max = weather.get('temp_max', 'N/A')
    temp_min = weather.get('temp_min', 'N/A')
    precipitation = weather.get('precipitation_sum', 0)
    wind_speed = weather.get('wind_speed_max', 'N/A')
    
    # Build complete message with localized headers/footers but original weather text
    if language == 'sk':
        if personality == 'emuska':
            header = f"💖 Ahoj moja drahá Emuška!\n\nPočasie pre {location} dnes:"
            footer = "\n---\n💕 S láskou, tvoja Daily Brief služba\nAk ma už nechceš, odpíš 'delete' 💔"
        elif personality == 'cute':
            header = f"🌟 Ahoj zlatko!\n\nPočasie pre {location} dnes:"
            footer = "\n---\n🎈 Služba Daily Brief | Zrušiť: Odpíš 'delete'"
        elif personality == 'brutal':
            header = f"Počasie - {location}"
            footer = "\n---\nDaily Brief | Zrušiť: 'delete'"
        else:  # neutral
            header = f"📊 Denná predpoveď počasia - {location}"
            footer = "\n---\nSlužba Daily Brief | Zrušiť odber: Odpíš 'delete'"
        
        weather_data = f"""• Maximum: {temp_max}°C
• Minimum: {temp_min}°C  
• Zrážky: {precipitation}mm
• Vietor: {wind_speed} km/h

{condition_message}"""

    elif language == 'es':
        if personality == 'cute':
            header = f"🌟 ¡Hola querido!\n\nClima para {location} hoy:"
            footer = "\n---\n💕 Servicio Daily Brief | Cancelar: Responde 'delete'"
        elif personality == 'brutal':
            header = f"Clima - {location}"
            footer = "\n---\nDaily Brief | Cancelar: 'delete'"
        else:  # neutral
            header = f"📊 Pronóstico diario - {location}"
            footer = "\n---\nServicio Daily Brief | Cancelar suscripción: Responde 'delete'"
            
        weather_data = f"""• Máxima: {temp_max}°C
• Mínima: {temp_min}°C  
• Precipitación: {precipitation}mm
• Viento: {wind_speed} km/h

{condition_message}"""

    else:  # English
        if personality == 'cute':
            header = f"🌟 Hello sunshine!\n\nWeather for {location} today:"
            footer = "\n---\n💖 Daily Brief Service | Unsubscribe: Reply 'delete'"
        elif personality == 'brutal':
            header = f"Weather - {location}"
            footer = "\n---\nDaily Brief | Unsubscribe: 'delete'"
        else:  # neutral
            header = f"📊 Daily Weather Forecast - {location}"
            footer = "\n---\nDaily Brief Service | Unsubscribe: Reply 'delete'"
            
        weather_data = f"""• High: {temp_max}°C
• Low: {temp_min}°C  
• Precipitation: {precipitation}mm
• Wind: {wind_speed} km/h

{condition_message}"""
    
    return f"{header}\n\n{weather_data}{footer}"

def send_proper_localized_weather(target_email):
    """Send weather email using the correct combination of systems."""
    
    print(f"📧 Sending properly localized weather email to: {target_email}")
    
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
    
    # Generate message using BOTH systems
    print(f"📝 Generating {language} message with {personality} personality using your weather_messages.txt...")
    message = generate_complete_weather_email(weather, location, personality, language)
    
    # Get localized subject from new system
    subject = get_localized_subject('daily_forecast_subject', personality, language, location=location)
    
    # Send email
    print("📤 Sending...")
    
    try:
        success = send_email(config, target_email, subject, message, dry_run=False)
        
        if success:
            print("✅ PROPERLY LOCALIZED EMAIL SENT!")
            print(f"\n📧 Subject: {subject}")
            print("\n📝 Message sent:")
            print("=" * 60)
            print(message)
            print("=" * 60)
            return True
        else:
            print("❌ Send failed")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    # Only test with your email - no real emails to other people!
    print("🇺🇸 Testing English brutal with your REAL weather_messages.txt")
    print("=" * 60)
    
    success = send_proper_localized_weather("filip.johanes9@gmail.com")
    
    if success:
        print("\n🎉 Email sent with REAL weather_messages.txt content!")
        print("📧 Only sent to filip.johanes9@gmail.com - no spam to other emails!")
    else:
        print("\n❌ Email failed")