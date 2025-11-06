#!/usr/bin/env python3
"""
Test Personality & Language Modes
Comprehensive testing of all personality modes and language support.
"""

import os
import sys
import sqlite3
import logging
from datetime import datetime
from typing import Dict, List

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import (
    Config, EmailMessageInfo, load_env, process_inbound_email, 
    handle_personality_command, handle_weather_command, 
    get_weather_message, load_weather_messages
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PersonalityLanguageTester:
    """Test personality modes and language support"""
    
    def __init__(self):
        self.config = load_env()
        self.test_email = "personality.tester@example.com"
        
        # Available personality modes
        self.personality_modes = ['neutral', 'cute', 'brutal', 'emuska']
        
        # Available languages
        self.languages = ['en', 'es', 'sk']
        
        # Weather conditions to test
        self.test_conditions = [
            'sunny', 'raining', 'snowing', 'hot', 'cold', 
            'windy', 'stormy', 'foggy', 'mild'
        ]
        
        print("🎭 Personality & Language Mode Tester")
        print("=" * 50)
    
    def clean_test_data(self):
        """Remove any existing test data"""
        try:
            conn = sqlite3.connect("app.db")
            conn.execute("DELETE FROM subscribers WHERE email = ?", (self.test_email,))
            conn.execute("DELETE FROM reminders WHERE email = ?", (self.test_email,))
            # Clean inbox_log if it exists (might not have sender column)
            try:
                conn.execute("DELETE FROM inbox_log WHERE sender = ?", (self.test_email,))
            except:
                # Try with email_hash if sender column doesn't exist
                pass
            conn.commit()
            conn.close()
            logger.info(f"Cleaned test data for {self.test_email}")
        except Exception as e:
            logger.error(f"Error cleaning test data: {e}")
    
    def test_weather_messages_by_language(self):
        """Test weather message loading for all languages"""
        print("\n🌍 Testing Weather Messages by Language")
        print("-" * 40)
        
        for language in self.languages:
            try:
                messages = load_weather_messages(language=language)
                print(f"✅ {language.upper()}: {len(messages)} weather conditions loaded")
                
                # Show a sample message for each personality
                if 'sunny' in messages:
                    sunny_messages = messages['sunny']
                    print(f"   Sample 'sunny' messages:")
                    for personality in ['neutral', 'cute', 'brutal']:
                        if personality in sunny_messages:
                            msg = sunny_messages[personality][:60] + "..." if len(sunny_messages[personality]) > 60 else sunny_messages[personality]
                            print(f"     {personality}: {msg}")
                    
                    # Special handling for Emuska (Slovak only)
                    if language == 'sk' and 'emuska' in sunny_messages:
                        msg = sunny_messages['emuska'][:60] + "..." if len(sunny_messages['emuska']) > 60 else sunny_messages['emuska']
                        print(f"     emuska: {msg}")
                    elif language != 'sk':
                        print(f"     emuska: [Only available in Slovak]")
                
            except Exception as e:
                print(f"❌ {language.upper()}: Error loading messages - {e}")
        
        print()
    
    def test_personality_mode_changes(self):
        """Test changing personality modes"""
        print("🎭 Testing Personality Mode Changes")
        print("-" * 40)
        
        # First subscribe to weather service
        print(f"📧 Subscribing {self.test_email} to weather service...")
        
        weather_msg = EmailMessageInfo(
            uid="test_weather_sub",
            from_email=self.test_email,
            subject="Prague, Czech Republic",
            plain_text_body="I want weather updates for Prague in Czech Republic",
            date=datetime.now()
        )
        
        try:
            process_inbound_email(self.config, weather_msg, dry_run=True)
            print("✅ Weather subscription processed")
        except Exception as e:
            print(f"❌ Weather subscription failed: {e}")
            return
        
        # Test each personality mode
        for mode in self.personality_modes:
            print(f"\n🎭 Testing personality mode: {mode}")
            
            try:
                # Special case: emuska only works with Slovak language
                if mode == 'emuska':
                    print("   Note: Emuska mode requires Slovak language")
                    # First change language to Slovak
                    lang_msg = EmailMessageInfo(
                        uid=f"test_lang_sk",
                        from_email=self.test_email,
                        subject="Language: sk",
                        plain_text_body="Change my language to Slovak please",
                        date=datetime.now()
                    )
                    process_inbound_email(self.config, lang_msg, dry_run=True)
                
                # Test personality change
                personality_msg = EmailMessageInfo(
                    uid=f"test_personality_{mode}",
                    from_email=self.test_email,
                    subject=f"Personality: {mode}",
                    plain_text_body=f"Change my personality to {mode}",
                    date=datetime.now()
                )
                
                process_inbound_email(self.config, personality_msg, dry_run=True)
                print(f"✅ Personality mode '{mode}' processed successfully")
                
                # Test sample weather message with this personality
                try:
                    lang = 'sk' if mode == 'emuska' else 'en'
                    sample_message = get_weather_message('sunny', mode, lang)
                    print(f"   Sample sunny message: {sample_message}")
                except Exception as e:
                    print(f"   ⚠️ Could not generate sample message: {e}")
                
            except Exception as e:
                print(f"❌ Personality mode '{mode}' failed: {e}")
        
        print()
    
    def test_language_changes(self):
        """Test changing languages"""
        print("🌍 Testing Language Changes")
        print("-" * 40)
        
        for language in self.languages:
            print(f"\n🗣️ Testing language: {language}")
            
            try:
                lang_msg = EmailMessageInfo(
                    uid=f"test_language_{language}",
                    from_email=self.test_email,
                    subject=f"Language: {language}",
                    plain_text_body=f"Please change my language to {language}",
                    date=datetime.now()
                )
                
                process_inbound_email(self.config, lang_msg, dry_run=True)
                print(f"✅ Language '{language}' processed successfully")
                
                # Test weather message in this language
                try:
                    messages = load_weather_messages(language=language)
                    if 'sunny' in messages and 'neutral' in messages['sunny']:
                        sample = messages['sunny']['neutral']
                        print(f"   Sample message: {sample}")
                    else:
                        print(f"   ⚠️ No sunny/neutral message found for {language}")
                except Exception as e:
                    print(f"   ⚠️ Could not load messages for {language}: {e}")
                
            except Exception as e:
                print(f"❌ Language '{language}' failed: {e}")
        
        print()
    
    def test_combined_personality_language(self):
        """Test combinations of personality and language"""
        print("🎭🌍 Testing Combined Personality & Language")
        print("-" * 40)
        
        test_combinations = [
            ('en', 'neutral'),
            ('en', 'cute'), 
            ('en', 'brutal'),
            ('es', 'neutral'),
            ('es', 'cute'),
            ('sk', 'neutral'),
            ('sk', 'emuska'),  # Special Slovak-only mode
        ]
        
        for language, personality in test_combinations:
            print(f"\n🧪 Testing {language} + {personality}")
            
            try:
                # First set language
                lang_msg = EmailMessageInfo(
                    uid=f"test_combo_lang_{language}_{personality}",
                    from_email=self.test_email,
                    subject=f"Language: {language}",
                    plain_text_body=f"Change language to {language}",
                    date=datetime.now()
                )
                process_inbound_email(self.config, lang_msg, dry_run=True)
                
                # Then set personality
                personality_msg = EmailMessageInfo(
                    uid=f"test_combo_pers_{language}_{personality}",
                    from_email=self.test_email,
                    subject=f"Personality: {personality}",
                    plain_text_body=f"Change personality to {personality}",
                    date=datetime.now()
                )
                process_inbound_email(self.config, personality_msg, dry_run=True)
                
                # Test weather message
                sample_message = get_weather_message('sunny', personality, language)
                print(f"   ✅ Sample: {sample_message}")
                
            except Exception as e:
                print(f"   ❌ Failed: {e}")
        
        print()
    
    def test_weather_condition_samples(self):
        """Test different weather conditions with personality modes"""
        print("🌦️ Testing Weather Conditions with Personalities")
        print("-" * 40)
        
        # Test with English cute mode
        try:
            messages = load_weather_messages(language='en')
            print("Sample messages in English 'cute' mode:")
            
            for condition in ['sunny', 'raining', 'snowing', 'cold', 'hot']:
                if condition in messages and 'cute' in messages[condition]:
                    message = messages[condition]['cute']
                    print(f"  {condition}: {message}")
                
        except Exception as e:
            print(f"❌ Error testing weather conditions: {e}")
        
        print()
    
    def run_all_tests(self):
        """Run all personality and language tests"""
        print("🚀 Starting Comprehensive Personality & Language Tests\n")
        
        # Clean any existing test data
        self.clean_test_data()
        
        # Run all test suites
        self.test_weather_messages_by_language()
        self.test_personality_mode_changes()
        self.test_language_changes()
        self.test_combined_personality_language()
        self.test_weather_condition_samples()
        
        # Clean up after tests
        self.clean_test_data()
        
        print("✅ All personality & language tests completed!")

def main():
    """Run the personality and language tests"""
    tester = PersonalityLanguageTester()
    
    while True:
        print("\nTest Options:")
        print("1. Run all tests")
        print("2. Test weather messages by language")
        print("3. Test personality mode changes")
        print("4. Test language changes")
        print("5. Test combined personality + language")
        print("6. Test weather condition samples")
        print("7. Exit")
        
        choice = input("\nSelect option (1-7): ").strip()
        
        if choice == "1":
            tester.run_all_tests()
        elif choice == "2":
            tester.test_weather_messages_by_language()
        elif choice == "3":
            tester.test_personality_mode_changes()
        elif choice == "4":
            tester.test_language_changes()
        elif choice == "5":
            tester.test_combined_personality_language()
        elif choice == "6":
            tester.test_weather_condition_samples()
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please select 1-7.")

if __name__ == "__main__":
    main()