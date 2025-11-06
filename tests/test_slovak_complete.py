#!/usr/bin/env python3
"""
Test Slovak language with all personality modes including Emuska validation.

This test validates:
1. Slovak language works with all 4 personality modes (neutral, cute, brutal, emuska)
2. Emuska mode is properly restricted to Slovak language only
3. Weather message generation works correctly for all Slovak personalities
4. Language validation prevents inappropriate Emuska usage
"""

import sys
import sqlite3
from pathlib import Path

# Add parent directory to Python path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from app import (
    load_weather_messages, 
    get_weather_message,
    generate_weather_summary,
    get_weather_forecast,
    Config
)

def test_slovak_language_support():
    """Test that Slovak language supports all personality modes."""
    print("🧪 Testing Slovak language support...")
    
    # Load Slovak messages
    messages = load_weather_messages(language='sk')
    
    # Test that Slovak has all expected personality modes
    expected_personalities = ['neutral', 'cute', 'brutal', 'emuska']
    test_conditions = ['raining', 'hot', 'cold']
    
    for condition in test_conditions:
        if condition in messages:
            for personality in expected_personalities:
                message = get_weather_message(condition, personality, messages, 'sk')
                if not message or message.strip() == '':
                    print(f"❌ Missing Slovak message for {condition}/{personality}")
                    return False
                else:
                    print(f"✅ Slovak {personality}: {condition} -> {message[:50]}...")
    
    print("✅ Slovak language supports all personality modes")
    return True

def test_emuska_language_restriction():
    """Test that Emuska mode is properly restricted to Slovak language."""
    print("\n🧪 Testing Emuska language restriction...")
    
    # Test Emuska with Slovak (should work)
    sk_messages = load_weather_messages(language='sk')
    sk_emuska = get_weather_message('raining', 'emuska', sk_messages, 'sk')
    
    if not sk_emuska or sk_emuska.strip() == '':
        print("❌ Emuska mode should work with Slovak language")
        return False
    else:
        print(f"✅ Emuska works with Slovak: {sk_emuska[:50]}...")
    
    # Test Emuska with English (should fallback)
    en_messages = load_weather_messages(language='en')
    en_emuska = get_weather_message('raining', 'emuska', en_messages, 'en')
    
    # Should fallback to cute since Emuska is not available in English
    expected_fallback = get_weather_message('raining', 'cute', en_messages, 'en')
    
    if en_emuska != expected_fallback:
        print("❌ Emuska with English should fallback to cute")
        return False
    else:
        print("✅ Emuska with English properly falls back to cute")
    
    # Test Emuska with Spanish (should fallback)
    es_messages = load_weather_messages(language='es')
    es_emuska = get_weather_message('raining', 'emuska', es_messages, 'es')
    
    # Should fallback to cute since Emuska is not available in Spanish
    expected_fallback = get_weather_message('raining', 'cute', es_messages, 'es')
    
    if es_emuska != expected_fallback:
        print("❌ Emuska with Spanish should fallback to cute")
        return False
    else:
        print("✅ Emuska with Spanish properly falls back to cute")
    
    print("✅ Emuska language restriction working correctly")
    return True

def test_slovak_princess_messages():
    """Test that Slovak Emuska messages are romantic/princess-like."""
    print("\n🧪 Testing Slovak princess messages...")
    
    messages = load_weather_messages(language='sk')
    romantic_keywords = ['drahý', 'princezná', 'emuška', 'anjelik', 'zlatíčko', 'srdiečko', 'pampúšik', 'poklad', 'najkrajší']
    
    test_conditions = ['raining', 'heavy_rain', 'snowing', 'hot', 'cold']
    found_romantic = False
    
    for condition in test_conditions:
        if condition in messages:
            emuska_msg = get_weather_message(condition, 'emuska', messages, 'sk')
            emuska_lower = emuska_msg.lower()
            
            for keyword in romantic_keywords:
                if keyword in emuska_lower:
                    print(f"✅ Found romantic keyword '{keyword}' in {condition}: {emuska_msg[:60]}...")
                    found_romantic = True
                    break
    
    if not found_romantic:
        print("❌ No romantic keywords found in Slovak Emuska messages")
        return False
    
    print("✅ Slovak Emuska messages contain romantic/princess content")
    return True

def test_weather_summary_generation():
    """Test complete weather summary generation with Slovak personalities."""
    print("\n🧪 Testing weather summary generation...")
    
    # Mock weather data (matching get_weather_forecast return structure)
    mock_weather = {
        'temp_max': 18.0,
        'temp_min': 12.0,
        'precipitation_sum': 0.0,
        'precipitation_probability': 20.0,
        'wind_speed_max': 10.2
    }
    
    personalities = ['neutral', 'cute', 'brutal', 'emuska']
    location = "Bratislava"
    
    for personality in personalities:
        try:
            summary = generate_weather_summary(mock_weather, location, personality, 'sk')
            if summary and len(summary.strip()) > 0:
                print(f"✅ Slovak {personality} summary generated: {len(summary)} chars")
            else:
                print(f"❌ Failed to generate Slovak {personality} summary")
                return False
        except Exception as e:
            print(f"❌ Error generating Slovak {personality} summary: {e}")
            return False
    
    print("✅ Weather summary generation works for all Slovak personalities")
    return True

def run_all_tests():
    """Run all Slovak language tests."""
    print("🚀 Starting Slovak Language Comprehensive Tests\n")
    
    tests = [
        test_slovak_language_support,
        test_emuska_language_restriction, 
        test_slovak_princess_messages,
        test_weather_summary_generation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ Test {test.__name__} failed")
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Slovak language tests passed!")
        return True
    else:
        print("💥 Some Slovak language tests failed!")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)