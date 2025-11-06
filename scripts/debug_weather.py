#!/usr/bin/env python3
"""Debug weather API and message generation"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import Config, load_env, get_weather_forecast, geocode_location
import json

def debug_weather():
    """Debug weather API response."""
    
    config = load_env()
    
    # Test location: Bratislava
    lat, lon = 48.1486, 17.1077
    
    print("🌤️ Testing weather API...")
    weather = get_weather_forecast(lat, lon, config.timezone)
    
    if weather:
        print("✅ Weather data received")
        print("📊 Weather data structure:")
        print(json.dumps(weather, indent=2))
    else:
        print("❌ No weather data")

if __name__ == "__main__":
    debug_weather()