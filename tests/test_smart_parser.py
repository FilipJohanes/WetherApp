#!/usr/bin/env python3
"""Test the new smart email parser"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import parse_plaintext

def test_parser():
    """Test various email formats"""
    
    print("🧪 TESTING SMART EMAIL PARSER")
    print("=" * 60)
    
    test_cases = [
        # Simple format (new user-friendly style)
        ("bratislava\nsk\nemuska", "Simple 3-line format"),
        ("bratislava sk emuska", "Single line format"),
        ("madrid es cute", "Spanish cute"),
        
        # Natural language
        ("hello, i want weather for bratislava in slovak with emuska", "Natural English"),
        ("please send me weather for Madrid in Spanish", "Natural with full language name"),
        ("I'd like weather forecast for Prague, cute personality", "Conversational"),
        
        # Old format (backward compatibility)
        ("location: Bratislava, Slovakia\nlanguage: sk\npersonality: emuska", "Old labeled format"),
        ("location: New York\nlanguage: en\npersonality: brutal", "Old format"),
        
        # Mixed formats
        ("Prague\nenglish\nbrutal", "Full language name"),
        ("Bratislava, Slovakia\nslovenčina\nemuska", "Native language name"),
        
        # Edge cases
        ("Madrid", "Just location"),
        ("sk", "Just language"),
        ("emuska", "Just personality"),
        ("delete", "Delete command"),
        ("unsubscribe", "Unsubscribe command"),
        
        # Multi-word locations
        ("New York\nen\nneutral", "Multi-word location"),
        ("San Francisco, CA\nes\ncute", "Location with state"),
        
        # Language variations
        ("Prague\nslovensky\nbrutal", "Slovak language variant"),
        ("Madrid\nespañol\ncute", "Spanish language native name"),
        
        # Personality synonyms
        ("London\nen\nsweet", "Synonym for cute"),
        ("Paris\nen\nharsh", "Synonym for brutal"),
        ("Rome\nstandard", "Synonym for neutral"),
        
        # Super simple
        ("bratislava emuska", "Just location + personality"),
        ("madrid español", "Just location + language"),
        ("new york", "Just location (multi-word)"),
    ]
    
    for email_body, description in test_cases:
        print(f"\n📧 {description}")
        print(f"Input: {repr(email_body)}")
        
        result = parse_plaintext(email_body)
        
        print(f"✅ Parsed:")
        print(f"   Command: {result.get('command')}")
        if 'location' in result:
            print(f"   Location: {result['location']}")
        if 'language' in result:
            print(f"   Language: {result['language']}")
        if 'personality' in result:
            print(f"   Personality: {result['personality']}")
        if 'mode' in result:
            print(f"   Mode: {result['mode']}")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("\n💡 Key Features:")
    print("   • No need for 'location:', 'language:' labels")
    print("   • Works with any word order")
    print("   • Supports natural language")
    print("   • Backward compatible with old format")
    print("   • Detects synonyms (sweet=cute, harsh=brutal)")
    print("   • Handles multi-word locations")

if __name__ == "__main__":
    test_parser()
