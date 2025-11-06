#!/usr/bin/env python3
"""Quick test of weather service functionality."""

import os
import sys
import pathlib
# Add parent directory to Python path
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from app import Config, get_weather_forecast, geocode_location, get_weather_message

def test_weather_service():
    print("🧪 Testing Daily Brief Service - Weather Functionality")
    print("=" * 50)
    
    # Set up test environment variables
    os.environ['EMAIL_ADDRESS'] = 'test@example.com'
    os.environ['EMAIL_PASSWORD'] = 'test_password'
    os.environ['IMAP_HOST'] = 'imap.gmail.com'
    os.environ['SMTP_HOST'] = 'smtp.gmail.com'
    os.environ['TZ'] = 'Europe/Bratislava'
    
    # Create test config
    config = Config()
    
    # Test 1: Geocoding
    print("\n1. Testing Location Geocoding:")
    locations_to_test = ['Prague, CZ', 'New York, NY', 'Madrid, Spain']
    
    for location_str in locations_to_test:
        location = geocode_location(location_str)
        if location:
            print(f"  ✅ {location_str} → {location[0]:.4f}, {location[1]:.4f}")
        else:
            print(f"  ❌ {location_str} → Failed")
    
    # Test 2: Weather API
    print("\n2. Testing Weather API:")
    prague_coords = geocode_location('Prague, CZ')
    if prague_coords:
        weather = get_weather_forecast(prague_coords[0], prague_coords[1], config.timezone)
        if weather:
            print("  ✅ Weather API working")
            print(f"  📊 Current temp: {weather.get('current_temperature', 'N/A')}°C")
            print(f"  🌤️ Current weather: {weather.get('current_weather_description', 'N/A')}")
        else:
            print("  ❌ Weather API failed")
    
    # Test 3: Message Generation
    print("\n3. Testing Message Generation:")
    personalities = ['neutral', 'cute', 'brutal', 'emuska']
    languages = ['en', 'es', 'sk']
    
    for personality in personalities[:2]:  # Test first 2 personalities
        for language in languages[:2]:  # Test first 2 languages
            if prague_coords and weather:
                msg = get_weather_message(weather, 'Prague, CZ', personality, language)
                if msg:
                    print(f"  ✅ {personality}/{language}: {len(msg)} chars")
                else:
                    print(f"  ❌ {personality}/{language}: Failed")
    
    print("\n🎉 Weather service test complete!")

if __name__ == "__main__":
    test_weather_service()