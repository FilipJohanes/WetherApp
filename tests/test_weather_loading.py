#!/usr/bin/env python3
"""Test loading weather messages from your files"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # Go up one level

from app import load_weather_messages

def test_weather_messages():
    """Test loading your actual weather_messages.txt files."""
    
    languages = ['en', 'es', 'sk']
    
    for language in languages:
        print(f"\n🌍 Testing {language.upper()} weather messages:")
        print("-" * 40)
        
        messages = load_weather_messages(language=language)
        
        if messages:
            print(f"✅ Loaded {len(messages)} weather conditions")
            
            # Test a few conditions
            test_conditions = ['sunny', 'raining', 'cold', 'default']
            
            for condition in test_conditions:
                if condition in messages:
                    personalities = messages[condition]
                    print(f"\n{condition}:")
                    for personality, message in personalities.items():
                        if message:  # Only show non-empty messages
                            truncated = message[:80] + "..." if len(message) > 80 else message
                            print(f"  {personality:8}: {truncated}")
                        else:
                            print(f"  {personality:8}: (empty)")
        else:
            print("❌ No messages loaded")
    
    # Test Slovak emuska specifically
    print("\n" + "=" * 60)
    print("🇸🇰 SLOVAK EMUSKA MESSAGES:")
    print("=" * 60)
    
    sk_messages = load_weather_messages(language='sk')
    
    emuska_conditions = ['sunny', 'raining', 'cold', 'hot', 'snowing']
    
    for condition in emuska_conditions:
        if condition in sk_messages and 'emuska' in sk_messages[condition]:
            emuska_msg = sk_messages[condition]['emuska']
            if emuska_msg:
                print(f"\n{condition.upper()}:")
                print(f"  💖 {emuska_msg}")

if __name__ == "__main__":
    test_weather_messages()