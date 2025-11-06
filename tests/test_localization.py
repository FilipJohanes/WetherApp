#!/usr/bin/env python3
"""Test the localization system"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # Go up one level

from localization import get_localized_message, get_localized_subject

def test_localization():
    """Test all language and personality combinations."""
    
    print("🌍 Testing Daily Brief Localization System")
    print("=" * 50)
    
    # Test languages and personalities
    languages = ['en', 'es', 'sk']
    personalities = ['neutral', 'cute', 'brutal', 'emuska']
    
    # Test welcome message
    print("\n📝 WELCOME MESSAGES:")
    print("-" * 30)
    for lang in languages:
        for personality in personalities:
            message = get_localized_message('welcome', personality, lang)
            print(f"{lang.upper()} | {personality:8} | {message[:80]}...")
    
    # Test weather conditions
    print("\n🌤️ WEATHER CONDITION MESSAGES:")
    print("-" * 30)
    conditions = ['sunny', 'rainy', 'cold', 'hot']
    
    for condition in conditions:
        print(f"\n{condition.upper()}:")
        for lang in languages:
            for personality in personalities:
                message = get_localized_message(condition, personality, lang)
                print(f"  {lang} | {personality:8} | {message[:60]}...")
    
    # Test subject lines
    print("\n📧 EMAIL SUBJECTS:")
    print("-" * 30)
    subjects = [
        ('daily_forecast_subject', {'location': 'Bratislava'}),
        ('subscription_subject', {}),
        ('unsubscribe_subject', {})
    ]
    
    for subject_key, params in subjects:
        print(f"\n{subject_key}:")
        for lang in languages:
            for personality in ['neutral', 'cute', 'brutal', 'emuska']:
                subject = get_localized_subject(subject_key, personality, lang, **params)
                print(f"  {lang} | {personality:8} | {subject}")
    
    # Test Slovak emuska mode specifically
    print("\n🇸🇰 SLOVAK EMUSKA MODE SAMPLES:")
    print("-" * 30)
    emuska_tests = ['welcome', 'sunny', 'rainy', 'subscription_confirmed']
    
    for key in emuska_tests:
        message = get_localized_message(key, 'emuska', 'sk', location='Bratislava')
        print(f"{key:20} | {message}")
    
    print("\n✅ Localization test complete!")

if __name__ == "__main__":
    test_localization()