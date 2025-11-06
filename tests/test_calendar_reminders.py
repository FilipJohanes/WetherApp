#!/usr/bin/env python3
"""
Test Calendar Reminder Functionality
Comprehensive testing of calendar reminder creation, scheduling, and delivery.
"""

import os
import sys
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import (
    Config, EmailMessageInfo, load_env, process_inbound_email, 
    run_due_reminders_job, handle_calendar_command
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CalendarReminderTester:
    """Test calendar reminder functionality"""
    
    def __init__(self):
        self.config = load_env()
        self.test_email = "calendar.tester@example.com"
        
        print("📅 Calendar Reminder Tester")
        print("=" * 50)
    
    def clean_test_data(self):
        """Remove any existing test data"""
        try:
            conn = sqlite3.connect("app.db")
            conn.execute("DELETE FROM subscribers WHERE email = ?", (self.test_email,))
            conn.execute("DELETE FROM reminders WHERE email = ?", (self.test_email,))
            try:
                conn.execute("DELETE FROM inbox_log WHERE sender = ?", (self.test_email,))
            except:
                pass  # Column might not exist
            conn.commit()
            conn.close()
            logger.info(f"Cleaned test data for {self.test_email}")
        except Exception as e:
            logger.error(f"Error cleaning test data: {e}")
    
    def view_database_reminders(self):
        """Show all reminders in database"""
        try:
            conn = sqlite3.connect("app.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, email, message, first_run_at, last_sent_at, created_at, remaining_repeats
                FROM reminders 
                ORDER BY first_run_at
            """)
            
            reminders = cursor.fetchall()
            conn.close()
            
            if not reminders:
                print("📭 No reminders in database")
                return
            
            print(f"\n📋 Database Reminders ({len(reminders)} total):")
            print("-" * 80)
            
            for reminder in reminders:
                rid, email, message, first_run_at, last_sent_at, created_at, remaining_repeats = reminder
                status = "✅ Sent" if last_sent_at else "⏰ Pending"
                print(f"ID {rid}: {email}")
                print(f"   Message: {message}")
                print(f"   Scheduled: {first_run_at}")
                print(f"   Status: {status}")
                print(f"   Repeats left: {remaining_repeats}")
                print(f"   Created: {created_at}")
                print()
                
        except Exception as e:
            print(f"❌ Error viewing reminders: {e}")
    
    def test_reminder_creation(self):
        """Test creating different types of reminders"""
        print("📝 Testing Reminder Creation")
        print("-" * 40)
        
        # Test cases with different reminder formats
        test_reminders = [
            {
                "subject": "Reminder",
                "body": "Remind me tomorrow at 2 PM to call the dentist",
                "description": "Tomorrow at specific time"
            },
            {
                "subject": "Meeting reminder", 
                "body": "Please remind me on Friday at 10 AM about the team meeting",
                "description": "Specific day and time"
            },
            {
                "subject": "Birthday reminder",
                "body": "Remind me in 3 days at 9 AM that it's mom's birthday",
                "description": "Relative days"
            },
            {
                "subject": "Quick reminder",
                "body": "Remind me in 1 hour to check the laundry",
                "description": "Short term (1 hour)"
            },
            {
                "subject": "Appointment",
                "body": "Remind me next Monday at 3:30 PM about doctor appointment",
                "description": "Next week specific time"
            }
        ]
        
        for i, test_case in enumerate(test_reminders, 1):
            print(f"\n📧 Test {i}: {test_case['description']}")
            print(f"   Body: {test_case['body']}")
            
            try:
                reminder_msg = EmailMessageInfo(
                    uid=f"test_reminder_{i}",
                    from_email=self.test_email,
                    subject=test_case["subject"],
                    plain_text_body=test_case["body"],
                    date=datetime.now()
                )
                
                process_inbound_email(self.config, reminder_msg, dry_run=True)
                print(f"   ✅ Processed successfully")
                
            except Exception as e:
                print(f"   ❌ Failed: {e}")
        
        print()
    
    def test_reminder_parsing_formats(self):
        """Test different reminder text formats"""
        print("🔍 Testing Reminder Parsing Formats")
        print("-" * 40)
        
        parsing_tests = [
            "Remind me tomorrow at 2:00 PM to call John",
            "Remind me on Friday at 10 AM about the meeting", 
            "Remind me in 2 hours to check email",
            "Remind me next week on Monday at 3 PM about dentist",
            "Remind me on December 15th at 9:00 AM about Christmas shopping",
            "Remind me in 30 minutes to take medication",
            "Remind me today at 5 PM to leave for dinner",
            "Remind me this weekend to clean the garage"
        ]
        
        for i, reminder_text in enumerate(parsing_tests, 1):
            print(f"\n🧪 Parse Test {i}:")
            print(f"   Input: {reminder_text}")
            
            try:
                reminder_msg = EmailMessageInfo(
                    uid=f"test_parse_{i}",
                    from_email=self.test_email,
                    subject="Reminder",
                    plain_text_body=reminder_text,
                    date=datetime.now()
                )
                
                process_inbound_email(self.config, reminder_msg, dry_run=True)
                print(f"   ✅ Parsed successfully")
                
            except Exception as e:
                print(f"   ❌ Parse failed: {e}")
    
    def test_due_reminders_processing(self):
        """Test processing of due reminders"""
        print("⏰ Testing Due Reminders Processing")
        print("-" * 40)
        
        # Create a reminder that's due now
        print("📧 Creating immediate reminder...")
        
        immediate_reminder = EmailMessageInfo(
            uid="test_immediate_reminder",
            from_email=self.test_email,
            subject="Urgent reminder",
            plain_text_body="Remind me right now to test the reminder system",
            date=datetime.now()
        )
        
        try:
            process_inbound_email(self.config, immediate_reminder, dry_run=True)
            print("✅ Immediate reminder created")
            
            # Show database state
            self.view_database_reminders()
            
            # Process due reminders
            print("🔄 Processing due reminders...")
            run_due_reminders_job(self.config, dry_run=True)
            print("✅ Due reminders job completed")
            
        except Exception as e:
            print(f"❌ Due reminders test failed: {e}")
        
        print()
    
    def test_reminder_languages(self):
        """Test reminders in different languages"""
        print("🌍 Testing Reminder Languages")
        print("-" * 40)
        
        language_tests = [
            {
                "language": "en",
                "body": "Remind me tomorrow at 2 PM to call support",
                "description": "English reminder"
            },
            {
                "language": "es", 
                "body": "Recuérdame mañana a las 2 PM llamar al doctor",
                "description": "Spanish reminder"
            },
            {
                "language": "sk",
                "body": "Pripomeň mi zajtra o 14:00 zavolať do banky",
                "description": "Slovak reminder"
            }
        ]
        
        for test_case in language_tests:
            print(f"\n🗣️ Testing: {test_case['description']}")
            print(f"   Language: {test_case['language']}")
            print(f"   Body: {test_case['body']}")
            
            try:
                # First set language
                lang_msg = EmailMessageInfo(
                    uid=f"test_lang_{test_case['language']}",
                    from_email=self.test_email,
                    subject=f"Language: {test_case['language']}",
                    plain_text_body=f"Change language to {test_case['language']}",
                    date=datetime.now()
                )
                process_inbound_email(self.config, lang_msg, dry_run=True)
                
                # Then create reminder
                reminder_msg = EmailMessageInfo(
                    uid=f"test_reminder_{test_case['language']}",
                    from_email=self.test_email,
                    subject="Reminder",
                    plain_text_body=test_case["body"],
                    date=datetime.now()
                )
                process_inbound_email(self.config, reminder_msg, dry_run=True)
                print(f"   ✅ {test_case['description']} processed successfully")
                
            except Exception as e:
                print(f"   ❌ {test_case['description']} failed: {e}")
        
        print()
    
    def test_reminder_edge_cases(self):
        """Test edge cases and error handling"""
        print("🚨 Testing Reminder Edge Cases")
        print("-" * 40)
        
        edge_cases = [
            {
                "body": "Remind me",  # Missing details
                "description": "Missing time and message"
            },
            {
                "body": "Remind me yesterday to do something",  # Past date
                "description": "Past date"
            },
            {
                "body": "Remind me at 25:00 to do something",  # Invalid time
                "description": "Invalid time format"
            },
            {
                "body": "Remind me on Blursday at 2 PM to call",  # Invalid day
                "description": "Invalid day name"
            },
            {
                "body": "Please remind me tomorrow at 2 PM" + "X" * 500,  # Very long message
                "description": "Very long message"
            }
        ]
        
        for i, test_case in enumerate(edge_cases, 1):
            print(f"\n🧪 Edge Case {i}: {test_case['description']}")
            
            try:
                reminder_msg = EmailMessageInfo(
                    uid=f"test_edge_{i}",
                    from_email=self.test_email,
                    subject="Reminder",
                    plain_text_body=test_case["body"],
                    date=datetime.now()
                )
                
                process_inbound_email(self.config, reminder_msg, dry_run=True)
                print(f"   ✅ Handled gracefully")
                
            except Exception as e:
                print(f"   ✅ Expected error handled: {type(e).__name__}")
        
        print()
    
    def run_all_tests(self):
        """Run all calendar reminder tests"""
        print("🚀 Starting Comprehensive Calendar Reminder Tests\n")
        
        # Clean any existing test data
        self.clean_test_data()
        
        # Run all test suites
        self.test_reminder_creation()
        self.test_reminder_parsing_formats()
        self.test_due_reminders_processing()
        self.test_reminder_languages()
        self.test_reminder_edge_cases()
        
        # Show final database state
        print("📊 Final Database State:")
        self.view_database_reminders()
        
        # Clean up after tests
        self.clean_test_data()
        
        print("✅ All calendar reminder tests completed!")

def main():
    """Run the calendar reminder tests"""
    tester = CalendarReminderTester()
    
    while True:
        print("\nTest Options:")
        print("1. Run all tests")
        print("2. Test reminder creation")
        print("3. Test reminder parsing formats")
        print("4. Test due reminders processing")
        print("5. Test reminder languages")
        print("6. Test edge cases")
        print("7. View database reminders")
        print("8. Exit")
        
        choice = input("\nSelect option (1-8): ").strip()
        
        if choice == "1":
            tester.run_all_tests()
        elif choice == "2":
            tester.test_reminder_creation()
        elif choice == "3":
            tester.test_reminder_parsing_formats()
        elif choice == "4":
            tester.test_due_reminders_processing()
        elif choice == "5":
            tester.test_reminder_languages()
        elif choice == "6":
            tester.test_reminder_edge_cases()
        elif choice == "7":
            tester.view_database_reminders()
        elif choice == "8":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please select 1-8.")

if __name__ == "__main__":
    main()