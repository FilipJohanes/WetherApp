#!/usr/bin/env python3
"""
Show exactly what emuska email would look like - NO SENDING!
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # Go up one level

from app import load_weather_messages
from localization import get_localized_subject

def preview_emuska_email():
    """Preview what the emuska email would look like."""
    
    print("💖 EMUSKA EMAIL PREVIEW - What em.solarova@gmail.com would receive")
    print("=" * 70)
    
    # Simulate user data
    email = "em.solarova@gmail.com"
    location = "Bratislava"
    personality = "emuska"
    language = "sk"
    
    # Simulate weather data (current Bratislava weather)
    weather = {
        'temp_max': 12.5,
        'temp_min': 3.9,
        'precipitation_sum': 0.0,
        'wind_speed_max': 17.9
    }
    
    # Determine condition (sunny since no precipitation and decent temp)
    condition = 'sunny'
    
    # Load Slovak weather messages
    print("📁 Loading Slovak weather_messages.txt...")
    sk_messages = load_weather_messages(language='sk')
    
    # Get the real emuska message from your file
    if 'sunny' in sk_messages and 'emuska' in sk_messages['sunny']:
        emuska_weather_msg = sk_messages['sunny']['emuska']
        print(f"✅ Found emuska message for '{condition}'")
    else:
        emuska_weather_msg = "Emuska message not found"
        print(f"❌ No emuska message for '{condition}'")
    
    # Get localized subject
    subject = get_localized_subject('daily_forecast_subject', personality, language, location=location)
    
    # Build the complete email as it would be sent
    header = f"💖 Ahoj moja drahá Emuška!\n\nPočasie pre {location} dnes:"
    
    weather_data = f"""• Maximum: {weather['temp_max']}°C
• Minimum: {weather['temp_min']}°C  
• Zrážky: {weather['precipitation_sum']}mm
• Vietor: {weather['wind_speed_max']} km/h

{emuska_weather_msg}"""
    
    footer = "\n---\n💕 S láskou, tvoja Daily Brief služba\nAk ma už nechceš, odpíš 'delete' 💔"
    
    complete_email = f"{header}\n\n{weather_data}{footer}"
    
    # Show the complete email
    print(f"\n📧 TO: {email}")
    print(f"📧 SUBJECT: {subject}")
    print("\n📝 EMAIL CONTENT:")
    print("╔" + "═" * 68 + "╗")
    for line in complete_email.split('\n'):
        print(f"║ {line:<66} ║")
    print("╚" + "═" * 68 + "╝")
    
    print(f"\n💖 PURE EMUSKA MESSAGE (from your weather_messages.txt):")
    print("─" * 50)
    print(emuska_weather_msg)
    print("─" * 50)
    
    # Show other emuska conditions too
    print(f"\n🌦️ OTHER EMUSKA CONDITIONS from your file:")
    print("─" * 50)
    
    sample_conditions = ['raining', 'cold', 'hot', 'snowing', 'windy']
    
    for condition in sample_conditions:
        if condition in sk_messages and 'emuska' in sk_messages[condition]:
            msg = sk_messages[condition]['emuska']
            if msg:
                print(f"\n{condition.upper()}:")
                print(f"💖 {msg}")
    
    print("\n" + "=" * 70)
    print("✅ This is EXACTLY what emuska would receive!")
    print("📧 (But we're not sending it - just showing you!)")

if __name__ == "__main__":
    preview_emuska_email()