#!/usr/bin/env python3
"""
Quick integration test for Slovak language with Emuska mode validation.
"""

import sys
import sqlite3
from pathlib import Path

# Add parent directory to Python path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from app import load_weather_messages, get_weather_message

def test_emuska_validation():
    """Quick test that Emuska validation works correctly."""
    
    print("🧪 Testing Emuska mode validation...")
    
    # Test 1: Slovak + Emuska should work
    sk_messages = load_weather_messages(language='sk')
    sk_emuska = get_weather_message('raining', 'emuska', sk_messages, 'sk')
    
    if 'drahý poklad' in sk_emuska:
        print("✅ Slovak + Emuska mode: Works correctly")
    else:
        print("❌ Slovak + Emuska mode: Failed")
        return False
    
    # Test 2: English + Emuska should fall back to cute
    en_messages = load_weather_messages(language='en')  
    en_emuska = get_weather_message('raining', 'emuska', en_messages, 'en')
    en_cute = get_weather_message('raining', 'cute', en_messages, 'en')
    
    if en_emuska == en_cute:
        print("✅ English + Emuska mode: Properly falls back to cute")
    else:
        print("❌ English + Emuska mode: Fallback failed")
        return False
    
    print("✅ All Emuska validation tests passed!")
    return True

if __name__ == "__main__":
    success = test_emuska_validation()
    if success:
        print("\n🎉 Slovak language integration successful!")
    else:
        print("\n💥 Slovak language integration failed!")
    sys.exit(0 if success else 1)