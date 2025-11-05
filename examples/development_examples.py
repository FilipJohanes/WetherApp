"""
Example usage and development utilities for Daily Brief Service.

This file demonstrates how to use the service programmatically
and includes utilities for development across multiple PCs.
"""

import os
import sys
import sqlite3
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from app import (
        parse_plaintext,
        generate_weather_summary,
        detect_weather_condition,
        load_weather_messages,
        init_db
    )
except ImportError as e:
    print(f"Error importing app modules: {e}")
    print("Make sure you're running this from the project directory")
    sys.exit(1)


def demonstrate_parsing():
    """Demonstrate email parsing functionality."""
    print("🔍 EMAIL PARSING EXAMPLES")
    print("=" * 50)
    
    test_cases = [
        "delete",
        "cute", 
        "Bratislava, Slovakia",
        "date=tomorrow\ntime=2pm\nmessage=Team meeting\nrepeat=2",
        "Prague\npersonality=brutal"
    ]
    
    for test in test_cases:
        result = parse_plaintext(test)
        print(f"Input: {repr(test[:30])}")
        print(f"Parsed: {result}")
        print("-" * 30)


def demonstrate_weather_personalities():
    """Show weather personality modes in action."""
    print("\n🎭 WEATHER PERSONALITY EXAMPLES")
    print("=" * 50)
    
    # Sample weather data
    weather_scenarios = [
        {
            'name': 'Rainy Day',
            'data': {
                'temp_max': 18, 'temp_min': 12,
                'precipitation_probability': 85, 'precipitation_sum': 8,
                'wind_speed_max': 25
            }
        },
        {
            'name': 'Hot Summer Day', 
            'data': {
                'temp_max': 33, 'temp_min': 22,
                'precipitation_probability': 10, 'precipitation_sum': 0,
                'wind_speed_max': 12
            }
        }
    ]
    
    for scenario in weather_scenarios:
        print(f"\n📊 {scenario['name']}")
        print("-" * 30)
        
        condition = detect_weather_condition(scenario['data'])
        print(f"Detected condition: {condition}")
        
        for personality in ['neutral', 'cute', 'brutal']:
            print(f"\n{personality.upper()} mode:")
            summary = generate_weather_summary(
                scenario['data'], 
                "Example City",
                personality
            )
            # Show just the weather message part
            lines = summary.split('\n')
            for line in lines:
                if line.startswith('💡') or line.startswith('👕') or line.startswith('🥶'):
                    print(f"  {line}")


def create_test_database():
    """Create a test database with sample data."""
    print("\n🗃️ CREATING TEST DATABASE")
    print("=" * 50)
    
    test_db_path = "test_app.db"
    
    # Remove existing test database
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # Initialize database
    init_db(test_db_path)
    print(f"✅ Created test database: {test_db_path}")
    
    # Add sample data
    conn = sqlite3.connect(test_db_path)
    try:
        # Sample subscribers
        sample_subscribers = [
            ('user1@example.com', 'Prague, CZ', 50.0755, 14.4378, 'neutral'),
            ('user2@example.com', 'Bratislava, SK', 48.1486, 17.1077, 'cute'),
            ('user3@example.com', 'Vienna, AT', 48.2082, 16.3738, 'brutal')
        ]
        
        for email, location, lat, lon, personality in sample_subscribers:
            conn.execute("""
                INSERT INTO subscribers (email, location, lat, lon, personality, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (email, location, lat, lon, personality, datetime.now().isoformat()))
        
        # Sample reminders
        future_time = datetime.now() + timedelta(hours=1)
        conn.execute("""
            INSERT INTO reminders (email, message, first_run_at, remaining_repeats, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            'user1@example.com',
            'Sample reminder message',
            future_time.isoformat(),
            2,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        print("✅ Added sample subscribers and reminders")
        
        # Show what was created
        subscribers = conn.execute("SELECT email, location, personality FROM subscribers").fetchall()
        print(f"\n📊 Sample subscribers ({len(subscribers)}):")
        for email, location, personality in subscribers:
            print(f"  {email} - {location} [{personality}]")
            
        reminders = conn.execute("SELECT email, message FROM reminders").fetchall()
        print(f"\n📅 Sample reminders ({len(reminders)}):")
        for email, message in reminders:
            print(f"  {email} - {message}")
            
    finally:
        conn.close()
    
    return test_db_path


def verify_weather_messages():
    """Verify weather messages configuration."""
    print("\n💬 WEATHER MESSAGES VERIFICATION")
    print("=" * 50)
    
    try:
        messages = load_weather_messages()
        print(f"✅ Loaded {len(messages)} weather conditions")
        
        # Check for required personality modes
        missing_modes = []
        for condition, modes in messages.items():
            for personality in ['neutral', 'cute', 'brutal']:
                if personality not in modes:
                    missing_modes.append(f"{condition}.{personality}")
        
        if missing_modes:
            print(f"⚠️  Missing personality modes: {missing_modes}")
        else:
            print("✅ All conditions have complete personality modes")
            
        # Show sample messages
        print("\n📝 Sample messages:")
        for condition in ['raining', 'sunny', 'cold'][:3]:
            if condition in messages:
                print(f"\n{condition.upper()}:")
                for personality, message in messages[condition].items():
                    print(f"  {personality}: {message[:50]}...")
                    
    except Exception as e:
        print(f"❌ Error loading weather messages: {e}")


def development_setup_check():
    """Check development environment setup."""
    print("\n🔧 DEVELOPMENT SETUP CHECK")
    print("=" * 50)
    
    checks = []
    
    # Check Python version
    if sys.version_info >= (3, 11):
        checks.append("✅ Python 3.11+ available")
    else:
        checks.append(f"❌ Python 3.11+ required, found {sys.version}")
    
    # Check required files
    required_files = [
        'app.py',
        'requirements.txt', 
        'weather_messages.txt',
        '.env.example',
        '.gitignore'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            checks.append(f"✅ {file} exists")
        else:
            checks.append(f"❌ {file} missing")
    
    # Check environment example
    if os.path.exists('.env.example'):
        with open('.env.example', 'r') as f:
            content = f.read()
            if 'EMAIL_ADDRESS' in content:
                checks.append("✅ .env.example has email configuration")
            else:
                checks.append("❌ .env.example missing email settings")
    
    for check in checks:
        print(f"  {check}")
    
    # Recommendations
    print(f"\n💡 DEVELOPMENT RECOMMENDATIONS:")
    print(f"  1. Copy .env.example to .env and configure email")
    print(f"  2. Install dev dependencies: pip install -r requirements-dev.txt") 
    print(f"  3. Run tests: python -m pytest tests/")
    print(f"  4. Use --dry-run for testing without sending emails")


if __name__ == "__main__":
    print("🚀 DAILY BRIEF SERVICE - DEVELOPMENT EXAMPLES")
    print("=" * 60)
    
    try:
        demonstrate_parsing()
        demonstrate_weather_personalities() 
        verify_weather_messages()
        create_test_database()
        development_setup_check()
        
        print(f"\n🎉 All examples completed successfully!")
        print(f"\n💡 Next steps:")
        print(f"   1. Configure your email in .env")
        print(f"   2. Test with: python app.py --send-test your@email.com")
        print(f"   3. Run service: python app.py")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print(f"Make sure you have all dependencies installed:")
        print(f"pip install -r requirements.txt")