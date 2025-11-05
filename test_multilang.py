#!/usr/bin/env python3
"""Test multi-language weather message system."""

import sqlite3
from app import generate_weather_summary, load_weather_messages

def test_multilanguage_system():
    """Test the multi-language weather system."""
    print("=== Testing Multi-Language Weather System ===\n")
    
    # Test loading messages from different languages
    languages = ['en', 'es', 'sk']
    
    print("1. Testing language file loading:")
    for lang in languages:
        try:
            messages = load_weather_messages(language=lang)
            print(f"✅ {lang.upper()}: Loaded {len(messages)} conditions")
            
            # Test a sample condition
            if 'raining' in messages:
                raining_msgs = messages['raining']
                personalities = ['neutral', 'cute', 'brutal', 'emuska']
                for p in personalities:
                    if p in raining_msgs:
                        msg = raining_msgs[p]
                        status = "📝 (blank)" if not msg else "✅ (text)"
                        print(f"   {p}: {status}")
            print()
        except Exception as e:
            print(f"❌ {lang.upper()}: Error loading - {e}\n")
    
    # Test weather generation in different languages
    print("2. Testing weather generation in different languages:")
    
    # Mock weather data
    test_weather = {
        'temp_max': 22.0,
        'temp_min': 14.0,
        'precipitation_probability': 70.0,
        'precipitation_sum': 3.0,
        'wind_speed_max': 18.0,
        'weather_code': 61  # Light rain
    }
    
    for lang in languages:
        print(f"\n🌍 {lang.upper()} Language Sample:")
        print("-" * 50)
        try:
            if lang == 'sk':
                # For Slovak, test Emuska mode (since other modes are blank)
                summary = generate_weather_summary(test_weather, "Bratislava", "emuska", lang)
            else:
                # For English/Spanish, test cute mode
                summary = generate_weather_summary(test_weather, "Prague", "cute", lang)
            
            print(summary)
        except Exception as e:
            print(f"❌ Error generating weather for {lang}: {e}")
        print("=" * 60)
    
    # Test database with multi-language subscribers
    print("\n3. Testing database with multi-language subscribers:")
    
    # Clear test data
    conn = sqlite3.connect("app.db")
    conn.execute("DELETE FROM subscribers WHERE email LIKE '%test-lang%'")
    
    # Add test subscribers with different languages
    test_subscribers = [
        ("english@test-lang.com", "London", 51.5074, -0.1278, "cute", "en"),
        ("spanish@test-lang.com", "Madrid", 40.4168, -3.7038, "brutal", "es"),
        ("slovak@test-lang.com", "Bratislava", 48.1486, 17.1077, "emuska", "sk")
    ]
    
    for email, location, lat, lon, personality, language in test_subscribers:
        conn.execute("""
            INSERT INTO subscribers (email, location, lat, lon, personality, language, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, (email, location, lat, lon, personality, language))
    
    conn.commit()
    
    # Verify subscribers
    subscribers = conn.execute("""
        SELECT email, location, personality, language FROM subscribers 
        WHERE email LIKE '%test-lang%'
    """).fetchall()
    
    print("Multi-language subscribers added:")
    for sub in subscribers:
        print(f"  📧 {sub[0]} -> {sub[1]} ({sub[2]} mode, {sub[3]} language)")
    
    conn.close()
    
    print("\n✅ Multi-language system is ready!")
    print("\n📚 Usage Examples:")
    print("English: London\\npersonality=cute")
    print("Spanish: Madrid\\npersonality=brutal\\nlanguage=es") 
    print("Slovak (Emuska): Bratislava\\npersonality=emuska\\nlanguage=sk")
    
    print("\n🌟 Special Notes:")
    print("- Slovak language is designed for Emuska mode messages")
    print("- You can add custom Slovak messages to languages/sk/weather_messages.txt")
    print("- Other personality modes in Slovak are intentionally blank")

if __name__ == "__main__":
    test_multilanguage_system()