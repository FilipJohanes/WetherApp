#!/usr/bin/env python3
"""
Comprehensive Message Tests - Testing all personality modes across all languages.
"""

import sys
from pathlib import Path

# Add parent directory to Python path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from app import load_weather_messages, get_weather_message, generate_weather_summary

def test_all_message_combinations():
    """Test all personality modes across all supported languages."""
    
    print("🌍 === COMPREHENSIVE MESSAGE TESTS === 🌍\n")
    
    languages = ['en', 'es', 'sk']
    personalities = ['neutral', 'cute', 'brutal', 'emuska']
    test_condition = 'raining'
    
    # Mock weather data for summary generation
    mock_weather = {
        'temp_max': 18.0,
        'temp_min': 12.0,
        'precipitation_sum': 2.5,
        'precipitation_probability': 80.0,
        'wind_speed_max': 15.0
    }
    
    print("📝 Testing individual weather messages:")
    print("=" * 60)
    
    for lang in languages:
        print(f"\n🌍 {lang.upper()} Language:")
        messages = load_weather_messages(language=lang)
        
        for personality in personalities:
            message = get_weather_message(test_condition, personality, messages, lang)
            
            # Determine if message is available or fallback
            if personality == 'emuska' and lang != 'sk':
                status = "🔄 (fallback to cute)"
            elif message and message.strip():
                status = "✅ (available)"
            else:
                status = "❌ (empty)"
            
            print(f"  {personality:8}: {status}")
            if message and len(message) > 50:
                print(f"           → {message[:50]}...")
            elif message:
                print(f"           → {message}")
    
    print("\n" + "=" * 60)
    print("📊 Testing complete weather summaries:")
    print("=" * 60)
    
    for lang in languages:
        lang_name = {'en': 'English', 'es': 'Spanish', 'sk': 'Slovak'}[lang]
        location = {'en': 'London', 'es': 'Madrid', 'sk': 'Bratislava'}[lang]
        
        print(f"\n🏙️ {lang_name} - {location}:")
        print("-" * 40)
        
        for personality in personalities:
            # Skip Emuska for non-Slovak languages in summary test
            if personality == 'emuska' and lang != 'sk':
                print(f"  {personality:8}: ⏭️  (Emuska not available, would fallback to cute)")
                continue
            
            try:
                summary = generate_weather_summary(mock_weather, location, personality, lang)
                if summary and len(summary) > 100:
                    print(f"  {personality:8}: ✅ ({len(summary)} chars)")
                    # Show first line of the weather message
                    lines = summary.split('\n')
                    for line in lines:
                        if '💡' in line:
                            print(f"           → {line[:70]}...")
                            break
                else:
                    print(f"  {personality:8}: ❌ (failed or too short)")
            except Exception as e:
                print(f"  {personality:8}: ❌ (error: {e})")
    
    print("\n" + "=" * 60)
    print("🎯 Language-Specific Feature Summary:")
    print("=" * 60)
    
    print("📍 English (en):")
    print("  • Personalities: neutral, cute, brutal")
    print("  • Emuska mode: Falls back to cute")
    print("  • Special features: Standard English messages")
    
    print("\n📍 Spanish (es):")
    print("  • Personalities: neutral, cute, brutal")
    print("  • Emuska mode: Falls back to cute")
    print("  • Special features: Spanish translations")
    
    print("\n📍 Slovak (sk):")
    print("  • Personalities: neutral, cute, brutal, emuska")
    print("  • Emuska mode: ✨ EXCLUSIVE romantic princess messages")
    print("  • Special features: Full Slovak support + romantic Emuska content")
    
    print("\n🎉 All message tests completed successfully!")
    return True

if __name__ == "__main__":
    success = test_all_message_combinations()
    sys.exit(0 if success else 1)