#!/usr/bin/env python3
"""
Safe testing of localization - DRY RUN mode only, no real emails sent!
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # Go up one level

from app import Config, load_env, get_weather_forecast, send_email, load_weather_messages
from localization import get_localized_subject
import sqlite3

def test_localization_dry_run():
    """Test all localizations without sending real emails."""
    
    print("🧪 LOCALIZATION TEST - DRY RUN (NO EMAILS SENT)")
    print("=" * 60)
    
    # Test data - simulating different users
    test_users = [
        ("filip.johanes9@gmail.com", "Bratislava, Slovakia", "brutal", "en"),
        ("test_spanish@example.com", "Madrid, Spain", "cute", "es"), 
        ("test_slovak@example.com", "Bratislava", "emuska", "sk"),
        ("test_neutral@example.com", "London", "neutral", "en")
    ]
    
    # Fake weather data for testing
    test_weather = {
        'temp_max': 12.5,
        'temp_min': 3.9,
        'precipitation_sum': 0.0,
        'wind_speed_max': 17.9
    }
    
    for email, location, personality, language in test_users:
        print(f"\n📧 Testing: {email}")
        print(f"📍 {location} | 🎭 {personality} | 🌍 {language}")
        print("-" * 50)
        
        # Load weather messages for this language
        weather_messages = load_weather_messages(language=language)
        
        # Get a sunny weather message (our test condition)
        if 'sunny' in weather_messages and personality in weather_messages['sunny']:
            weather_msg = weather_messages['sunny'][personality]
        else:
            weather_msg = f"Weather message not found for {personality} in {language}"
        
        # Get localized subject
        subject = get_localized_subject('daily_forecast_subject', personality, language, location=location)
        
        # Build test message
        if language == 'sk':
            if personality == 'emuska':
                header = f"💖 Ahoj moja drahá Emuška!\n\nPočasie pre {location} dnes:"
                footer = "\n---\n💕 S láskou, tvoja Daily Brief služba"
            else:
                header = f"📊 Denná predpoveď počasia - {location}"
                footer = "\n---\nSlužba Daily Brief"
            
            weather_data = f"""• Maximum: {test_weather['temp_max']}°C
• Minimum: {test_weather['temp_min']}°C  
• Zrážky: {test_weather['precipitation_sum']}mm
• Vietor: {test_weather['wind_speed_max']} km/h

{weather_msg}"""

        elif language == 'es':
            header = f"📊 Pronóstico diario - {location}"
            footer = "\n---\nServicio Daily Brief"
            
            weather_data = f"""• Máxima: {test_weather['temp_max']}°C
• Mínima: {test_weather['temp_min']}°C  
• Precipitación: {test_weather['precipitation_sum']}mm
• Viento: {test_weather['wind_speed_max']} km/h

{weather_msg}"""

        else:  # English
            header = f"📊 Daily Weather Forecast - {location}"
            footer = "\n---\nDaily Brief Service"
            
            weather_data = f"""• High: {test_weather['temp_max']}°C
• Low: {test_weather['temp_min']}°C  
• Precipitation: {test_weather['precipitation_sum']}mm
• Wind: {test_weather['wind_speed_max']} km/h

{weather_msg}"""
        
        full_message = f"{header}\n\n{weather_data}{footer}"
        
        print(f"📧 Subject: {subject}")
        print(f"📝 Message Preview:")
        print(full_message[:200] + "..." if len(full_message) > 200 else full_message)
        
        if personality == 'emuska' and language == 'sk':
            print("💖 EMUSKA MESSAGE SAMPLE:")
            print(f"   {weather_msg}")
    
    print("\n" + "=" * 60)
    print("✅ DRY RUN COMPLETE - No real emails were sent!")
    print("📧 To send a real email, use: python send_hybrid_weather.py")

if __name__ == "__main__":
    test_localization_dry_run()