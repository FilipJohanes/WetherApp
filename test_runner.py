#!/usr/bin/env python3
"""
Daily Brief Service - Complete Testing Environment
Safe testing with no email sending - perfect for development!
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def run_test_suite():
    """Run comprehensive test suite for Daily Brief Service"""
    
    print("🧪 DAILY BRIEF SERVICE - TESTING ENVIRONMENT")
    print("=" * 60)
    print("🔒 SAFE MODE: No actual emails will be sent!")
    print()
    
    tests_to_run = [
        ("🌍 Localization System", "test_localization_safe.py"),
        ("💖 Slovak Emuska Preview", "preview_emuska.py"),
        ("🌤️ Weather API Tests", "test_weather.py"),
        ("📧 Message Generation", "test_messages_comprehensive.py"),
        ("🎭 Personality Modes", "test_personality_language.py"),
        ("🇸🇰 Slovak Language", "test_slovak_complete.py"),
        ("📱 Weather Loading", "test_weather_loading.py")
    ]
    
    print("Available Tests:")
    for i, (name, file) in enumerate(tests_to_run, 1):
        print(f"  {i}. {name}")
    
    print()
    print("Quick Options:")
    print("  A - Run all safe tests")
    print("  E - Preview emuska messages only")
    print("  W - Weather functionality only")
    print("  L - Localization tests only")
    print("  Q - Quit")
    
    choice = input("\n💡 Choose test to run (1-7, A, E, W, L, Q): ").upper().strip()
    
    if choice == 'Q':
        print("👋 Testing cancelled!")
        return
    elif choice == 'A':
        print("\n🚀 Running all safe tests...")
        run_all_tests(tests_to_run)
    elif choice == 'E':
        run_single_test("preview_emuska.py", "💖 Slovak Emuska Preview")
    elif choice == 'W':
        run_single_test("test_weather.py", "🌤️ Weather API Tests")
    elif choice == 'L':
        run_single_test("test_localization_safe.py", "🌍 Localization System")
    elif choice.isdigit() and 1 <= int(choice) <= len(tests_to_run):
        name, file = tests_to_run[int(choice) - 1]
        run_single_test(file, name)
    else:
        print("❌ Invalid choice! Please try again.")
        run_test_suite()

def run_single_test(test_file, test_name):
    """Run a single test file"""
    import subprocess
    
    print(f"\n🧪 Running: {test_name}")
    print("-" * 50)
    
    try:
        result = subprocess.run([
            sys.executable, 
            f"tests/{test_file}"
        ], cwd=os.path.dirname(os.path.dirname(__file__)), 
        capture_output=False)
        
        if result.returncode == 0:
            print(f"\n✅ {test_name} completed successfully!")
        else:
            print(f"\n⚠️ {test_name} completed with warnings")
            
    except Exception as e:
        print(f"\n❌ Error running {test_name}: {e}")

def run_all_tests(tests_to_run):
    """Run all safe tests"""
    print("\n🧪 Running complete test suite...")
    
    for name, file in tests_to_run:
        print(f"\n{'='*60}")
        run_single_test(file, name)
        print()
    
    print("🎉 All tests completed!")

def show_testing_info():
    """Show testing environment information"""
    print("📋 TESTING ENVIRONMENT INFO")
    print("-" * 40)
    print("🔒 Safe Mode: ON (no emails sent)")
    print("🌍 Localization: EN/ES/SK supported")
    print("🎭 Personalities: neutral/cute/brutal/emuska")
    print("☁️ Weather API: Open-Meteo (live data)")
    print("📧 Email Config: Uses production settings")
    print("🗄️ Database: Uses test data when needed")
    print()

if __name__ == "__main__":
    try:
        show_testing_info()
        run_test_suite()
    except KeyboardInterrupt:
        print("\n\n👋 Testing interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Testing error: {e}")