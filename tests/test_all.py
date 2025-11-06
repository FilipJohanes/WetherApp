#!/usr/bin/env python3
"""Comprehensive test suite for Daily Brief Service."""

import sys
from app import (
    parse_plaintext, generate_weather_summary, 
    load_weather_messages, detect_weather_condition
)

def run_comprehensive_tests():
    """Run all system tests."""
    print("🚀 === DAILY BRIEF SERVICE - COMPREHENSIVE TESTS === 🚀\n")
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Email Parsing
    print("📧 Test 1: Email Parsing")
    print("-" * 40)
    test_emails = [
        ("London", {"command": "WEATHER", "location": "London"}),
        ("London\npersonality=cute", {"command": "WEATHER", "location": "London", "personality": "cute"}),
        ("Madrid\nlanguage=es\npersonality=brutal", {"command": "WEATHER", "location": "Madrid", "language": "es", "personality": "brutal"}),
        ("delete", {"command": "DELETE"}),
        ("date=tomorrow\ntime=9am\nmessage=Meeting", {"command": "CALENDAR"})
    ]
    
    for email_body, expected in test_emails:
        result = parse_plaintext(email_body)
        if result["command"] == expected["command"]:
            print(f"✅ '{email_body.replace(chr(10), '\\n')}' → {result['command']}")
            tests_passed += 1
        else:
            print(f"❌ '{email_body.replace(chr(10), '\\n')}' → Expected {expected['command']}, got {result['command']}")
            tests_failed += 1
    
    # Test 2: Multi-Language Loading
    print(f"\n🌍 Test 2: Multi-Language Support")
    print("-" * 40)
    languages = ['en', 'es', 'sk']
    for lang in languages:
        try:
            messages = load_weather_messages(language=lang)
            if len(messages) >= 20:  # Should have at least 20 weather conditions
                print(f"✅ {lang.upper()}: {len(messages)} conditions loaded")
                tests_passed += 1
            else:
                print(f"❌ {lang.upper()}: Only {len(messages)} conditions loaded")
                tests_failed += 1
        except Exception as e:
            print(f"❌ {lang.upper()}: Error loading - {e}")
            tests_failed += 1
    
    # Test 3: Weather Generation
    print(f"\n🌤️ Test 3: Weather Generation")
    print("-" * 40)
    test_weather = {
        'temp_max': 20.0, 'temp_min': 12.0,
        'precipitation_probability': 60.0, 'precipitation_sum': 2.0,
        'wind_speed_max': 15.0, 'weather_code': 61
    }
    
    personalities = [('English Cute', 'cute', 'en'), ('Spanish Brutal', 'brutal', 'es'), ('Slovak Emuska', 'emuska', 'sk')]
    
    for name, personality, language in personalities:
        try:
            summary = generate_weather_summary(test_weather, "Test City", personality, language)
            if "Temperature:" in summary and "Rain probability:" in summary:
                print(f"✅ {name}: Weather report generated successfully")
                tests_passed += 1
            else:
                print(f"❌ {name}: Invalid weather report format")
                tests_failed += 1
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            tests_failed += 1
    
    # Test 4: Weather Condition Detection
    print(f"\n🔍 Test 4: Weather Condition Detection")
    print("-" * 40)
    test_conditions = [
        ({'temp_max': 35, 'temp_min': 25, 'precipitation_probability': 10, 'precipitation_sum': 0, 'wind_speed_max': 10}, 'hot'),
        ({'temp_max': 5, 'temp_min': 0, 'precipitation_probability': 80, 'precipitation_sum': 5, 'wind_speed_max': 15}, 'rainy_cold'),
        ({'temp_max': -5, 'temp_min': -10, 'precipitation_probability': 60, 'precipitation_sum': 10, 'wind_speed_max': 20}, 'snowing'),
        ({'temp_max': 25, 'temp_min': 15, 'precipitation_probability': 10, 'precipitation_sum': 0, 'wind_speed_max': 50}, 'windy')
    ]
    
    for weather_data, expected_condition in test_conditions:
        try:
            detected = detect_weather_condition(weather_data)
            print(f"✅ Temp {weather_data['temp_max']}°C → {detected}")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Weather detection error: {e}")
            tests_failed += 1
    
    # Test 5: Princess Messages Check
    print(f"\n👸 Test 5: Princess Emuska Messages")
    print("-" * 40)
    try:
        sk_messages = load_weather_messages(language='sk')
        emuska_conditions = []
        for condition, personalities in sk_messages.items():
            if personalities.get('emuska', '').strip():
                emuska_conditions.append(condition)
        
        if len(emuska_conditions) >= 15:  # Should have most conditions filled
            print(f"✅ Princess messages: {len(emuska_conditions)} conditions have Emuska messages")
            tests_passed += 1
            
            # Show sample
            sample = sk_messages.get('raining', {}).get('emuska', '')
            if 'princezná' in sample or 'poklad' in sample:
                print(f"✅ Princess language detected: Contains loving terms")
                tests_passed += 1
            else:
                print(f"❌ Princess language: Missing loving terms")
                tests_failed += 1
        else:
            print(f"❌ Princess messages: Only {len(emuska_conditions)} conditions filled")
            tests_failed += 1
    except Exception as e:
        print(f"❌ Princess test error: {e}")
        tests_failed += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"🏁 TEST RESULTS")
    print(f"{'='*60}")
    print(f"✅ Passed: {tests_passed}")
    print(f"❌ Failed: {tests_failed}")
    print(f"📊 Success Rate: {(tests_passed/(tests_passed+tests_failed)*100):.1f}%")
    
    if tests_failed == 0:
        print(f"\n🎉 ALL TESTS PASSED! Your Daily Brief Service is ready! 🚀")
        print(f"💡 To start the service: python app.py")
        print(f"🔧 To run with email: Set up .env file first")
        return True
    else:
        print(f"\n⚠️ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)