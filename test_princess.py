#!/usr/bin/env python3
"""Test the romantic Emuska messages for your princess! 💕"""

from app import generate_weather_summary, load_weather_messages

def test_emuska_messages():
    """Test the beautiful princess messages for Emuska."""
    print("💕 === Testing Princess Emuska Messages === 👸\n")
    
    # Load Slovak messages
    messages = load_weather_messages(language='sk')
    
    # Test different weather conditions for Emuska
    test_scenarios = [
        {
            'weather': {
                'temp_max': 22.0, 'temp_min': 15.0,
                'precipitation_probability': 70.0, 'precipitation_sum': 3.0,
                'wind_speed_max': 12.0, 'weather_code': 61
            },
            'condition': 'Rainy day in Bratislava'
        },
        {
            'weather': {
                'temp_max': 28.0, 'temp_min': 20.0,
                'precipitation_probability': 10.0, 'precipitation_sum': 0.0,
                'wind_speed_max': 8.0, 'weather_code': 0
            },
            'condition': 'Sunny day for princess'
        },
        {
            'weather': {
                'temp_max': 5.0, 'temp_min': -2.0,
                'precipitation_probability': 20.0, 'precipitation_sum': 0.0,
                'wind_speed_max': 15.0, 'weather_code': 1
            },
            'condition': 'Cold day - need warm hugs'
        }
    ]
    
    print("🌹 Sample Emuska messages from different conditions:")
    print("=" * 60)
    
    # Show sample messages
    sample_conditions = ['raining', 'sunny', 'cold', 'hot', 'default']
    for condition in sample_conditions:
        if condition in messages and 'emuska' in messages[condition]:
            emuska_msg = messages[condition]['emuska']
            print(f"🌸 {condition.upper()}:")
            print(f"   💕 {emuska_msg}")
            print()
    
    print("=" * 60)
    print("🏰 Full weather reports for Princess Emuska:")
    print("=" * 60)
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n👑 Scenario {i}: {scenario['condition']}")
        print("-" * 50)
        summary = generate_weather_summary(
            scenario['weather'], 
            "Bratislava", 
            "emuska", 
            "sk"
        )
        print(summary)
        print("💖" * 20)

if __name__ == "__main__":
    test_emuska_messages()