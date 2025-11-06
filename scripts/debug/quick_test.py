#!/usr/bin/env python3
"""Quick test of Emuska mode alongside other personalities."""

from app import generate_weather_summary

# Mock weather data
test_weather = {
    'temp_max': 18.0,
    'temp_min': 10.0,
    'precipitation_probability': 40.0,
    'precipitation_sum': 1.0,
    'wind_speed_max': 12.0,
    'weather_code': 61  # Light rain
}

print("=== All Personality Modes Comparison ===\n")

personalities = ['neutral', 'cute', 'brutal', 'emuska']

for personality in personalities:
    print(f"🎭 {personality.upper()} MODE:")
    print("-" * 50)
    summary = generate_weather_summary(test_weather, "Prague", personality)
    print(summary)
    print("=" * 60)
    print()