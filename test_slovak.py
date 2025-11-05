#!/usr/bin/env python3
"""Test the updated Slovak weather messages."""

from app import generate_weather_summary, load_weather_messages

def test_slovak_messages():
    """Test Slovak weather messages with all personalities."""
    print("=== Testing Updated Slovak Messages ===\n")
    
    # Test loading Slovak messages
    messages = load_weather_messages(language='sk')
    print(f"✅ Loaded {len(messages)} Slovak weather conditions")
    
    # Test sample conditions
    sample_conditions = ['raining', 'sunny', 'cold', 'default']
    
    for condition in sample_conditions:
        if condition in messages:
            print(f"\n🌤️ Condition: {condition}")
            print("-" * 40)
            personalities = ['neutral', 'cute', 'brutal', 'emuska']
            for personality in personalities:
                msg = messages[condition].get(personality, '')
                status = "📝 (blank)" if not msg else "✅ (filled)"
                print(f"  {personality:8}: {status}")
                if msg:  # Show first 50 chars if message exists
                    preview = msg[:50] + "..." if len(msg) > 50 else msg
                    print(f"           {preview}")
    
    # Test weather generation with different personalities
    print("\n" + "="*60)
    print("🧪 Testing Weather Generation:")
    
    test_weather = {
        'temp_max': 15.0,
        'temp_min': 5.0,
        'precipitation_probability': 80.0,
        'precipitation_sum': 4.0,
        'wind_speed_max': 20.0,
        'weather_code': 61  # Light rain
    }
    
    personalities = ['neutral', 'cute', 'brutal']  # Skip emuska (blank)
    
    for personality in personalities:
        print(f"\n🎭 Slovak {personality.upper()} mode:")
        print("-" * 50)
        summary = generate_weather_summary(test_weather, "Bratislava", personality, "sk")
        print(summary)

if __name__ == "__main__":
    test_slovak_messages()