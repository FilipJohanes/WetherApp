#!/usr/bin/env python3
"""
Safe Webhook Simulator - No Network Required
Simulates webhook functionality using file-based input/output.
Perfect for testing on company computers without network concerns.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Optional

# Import existing functions from the original app
from app import (
    Config, EmailMessageInfo, load_env, process_inbound_email,
    should_process_email
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SafeWebhookSimulator:
    """Simulate webhook processing without network exposure"""
    
    def __init__(self):
        self.config = load_env()
        self.input_folder = "webhook_input"
        self.output_folder = "webhook_output"
        
        # Create folders if they don't exist
        os.makedirs(self.input_folder, exist_ok=True)
        os.makedirs(self.output_folder, exist_ok=True)
    
    def process_email_file(self, filename: str) -> Dict:
        """Process a JSON email file"""
        input_path = os.path.join(self.input_folder, filename)
        
        if not os.path.exists(input_path):
            return {"error": f"File {filename} not found"}
        
        try:
            # Read email data from JSON file
            with open(input_path, 'r', encoding='utf-8') as f:
                email_data = json.load(f)
            
            logger.info(f"Processing email file: {filename}")
            
            # Convert to EmailMessageInfo format
            msg_info = EmailMessageInfo(
                sender=email_data.get('from', ''),
                subject=email_data.get('subject', ''),
                body=email_data.get('body', ''),
                timestamp=datetime.now(),
                uid=email_data.get('message_id', filename)
            )
            
            # Check if we should process this email
            if not should_process_email(msg_info.sender, msg_info.subject, msg_info.body):
                result = {
                    "status": "filtered",
                    "reason": "Email filtered by processing rules",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Process using existing function (dry run)
                try:
                    process_inbound_email(self.config, msg_info, dry_run=True)
                    result = {
                        "status": "success",
                        "message": "Email processed successfully (DRY RUN)",
                        "timestamp": datetime.now().isoformat()
                    }
                except Exception as e:
                    result = {
                        "status": "error", 
                        "message": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
            
            # Save result to output file
            output_filename = f"result_{filename}"
            output_path = os.path.join(self.output_folder, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "input": email_data,
                    "result": result
                }, f, indent=2)
            
            logger.info(f"Result saved to: {output_filename}")
            return result
            
        except Exception as e:
            error_result = {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
            logger.error(f"Error processing {filename}: {e}")
            return error_result
    
    def process_all_files(self):
        """Process all JSON files in input folder"""
        json_files = [f for f in os.listdir(self.input_folder) if f.endswith('.json')]
        
        if not json_files:
            logger.info("No JSON files found in webhook_input folder")
            return
        
        logger.info(f"Found {len(json_files)} email files to process")
        
        for filename in json_files:
            result = self.process_email_file(filename)
            print(f"✅ {filename}: {result['status']}")
    
    def create_sample_emails(self):
        """Create sample email files for testing"""
        samples = [
            {
                "from": "test.user@example.com",
                "subject": "Prague, Czech Republic",
                "body": "Hi, I would like to subscribe to daily weather updates for Prague. Thank you!",
                "message_id": "test_weather_subscription"
            },
            {
                "from": "calendar.user@example.com", 
                "subject": "Reminder",
                "body": "Please remind me tomorrow at 2 PM to call the dentist for appointment scheduling.",
                "message_id": "test_calendar_reminder"
            },
            {
                "from": "personality.test@example.com",
                "subject": "Personality: casual",
                "body": "Change my personality mode to casual please",
                "message_id": "test_personality_change"
            },
            {
                "from": "unsubscribe.user@example.com",
                "subject": "Unsubscribe",
                "body": "Please unsubscribe me from weather updates",
                "message_id": "test_unsubscribe"
            },
            {
                "from": "no-reply@google.com",
                "subject": "Security Alert",
                "body": "We noticed unusual activity on your account",
                "message_id": "test_system_email"
            }
        ]
        
        for i, sample in enumerate(samples, 1):
            filename = f"sample_email_{i}.json"
            filepath = os.path.join(self.input_folder, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(sample, f, indent=2)
            
            logger.info(f"Created sample email: {filename}")
        
        print(f"✅ Created {len(samples)} sample email files in {self.input_folder}/")

def main():
    """Run the safe webhook simulator"""
    simulator = SafeWebhookSimulator()
    
    print("🔒 Safe Webhook Simulator - No Network Required")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Create sample email files")
        print("2. Process all email files")
        print("3. Process specific file")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            simulator.create_sample_emails()
        
        elif choice == "2":
            simulator.process_all_files()
        
        elif choice == "3":
            filename = input("Enter filename (e.g., sample_email_1.json): ").strip()
            result = simulator.process_email_file(filename)
            print(f"Result: {json.dumps(result, indent=2)}")
        
        elif choice == "4":
            print("Goodbye!")
            break
        
        else:
            print("Invalid option. Please select 1-4.")

if __name__ == "__main__":
    main()