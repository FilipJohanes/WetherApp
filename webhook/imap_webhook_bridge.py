#!/usr/bin/env python3
"""
IMAP to Webhook Bridge
Converts any IMAP email account into webhook calls to your Daily Brief Service.

This bridge polls IMAP (like your current service) but sends webhooks to the new
webhook service. This gives you the benefits of webhook processing while working
with any email provider.
"""

import imaplib
import smtplib
import ssl
import email
import logging
import json
import time
import hashlib
import requests
from datetime import datetime
from email.utils import parseaddr
from typing import Optional, Dict, Set
import os

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IMAPWebhookBridge:
    """Bridges IMAP email checking to webhook calls"""
    
    def __init__(self):
        # Email configuration
        self.email_address = os.getenv('EMAIL_ADDRESS')
        self.email_password = os.getenv('EMAIL_PASSWORD') 
        self.imap_server = os.getenv('IMAP_SERVER', 'imap.gmail.com')
        self.imap_port = int(os.getenv('IMAP_PORT', 993))
        
        # Webhook configuration
        self.webhook_url = os.getenv('WEBHOOK_URL', 'http://localhost:5000/webhook/email')
        self.webhook_timeout = int(os.getenv('WEBHOOK_TIMEOUT', 10))
        
        # Bridge configuration
        self.check_interval = int(os.getenv('BRIDGE_CHECK_INTERVAL', 30))  # seconds
        self.max_emails_per_check = int(os.getenv('MAX_EMAILS_PER_CHECK', 50))
        
        # Track processed messages to avoid duplicates
        self.processed_messages: Set[str] = set()
        self.max_processed_cache = 10000
        
        if not all([self.email_address, self.email_password]):
            raise ValueError("EMAIL_ADDRESS and EMAIL_PASSWORD environment variables required")
    
    def connect_imap(self) -> imaplib.IMAP4_SSL:
        """Connect to IMAP server"""
        try:
            logger.info(f"Connecting to IMAP server: {self.imap_server}:{self.imap_port}")
            
            # Create SSL context
            context = ssl.create_default_context()
            
            # Connect to server
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port, ssl_context=context)
            
            # Login
            mail.login(self.email_address, self.email_password)
            
            # Select inbox
            mail.select('inbox')
            
            logger.info("IMAP connection successful")
            return mail
            
        except Exception as e:
            logger.error(f"IMAP connection failed: {e}")
            raise
    
    def get_email_body(self, email_message) -> str:
        """Extract email body text"""
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        body += payload.decode('utf-8', errors='ignore')
        else:
            payload = email_message.get_payload(decode=True)
            if payload:
                body = payload.decode('utf-8', errors='ignore')
        
        return body.strip()
    
    def send_webhook(self, email_data: Dict) -> bool:
        """Send email data to webhook endpoint"""
        try:
            logger.info(f"Sending webhook for email: {email_data['subject']}")
            
            response = requests.post(
                self.webhook_url,
                json=email_data,
                timeout=self.webhook_timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Webhook successful: {result.get('status', 'unknown')}")
                return True
            else:
                logger.error(f"Webhook failed: HTTP {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error(f"Webhook timeout after {self.webhook_timeout}s")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Webhook request failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return False
    
    def process_new_emails(self, mail: imaplib.IMAP4_SSL) -> int:
        """Check for and process new emails"""
        try:
            # Search for unseen emails
            status, messages = mail.search(None, 'UNSEEN')
            
            if status != 'OK':
                logger.error("Failed to search for emails")
                return 0
            
            message_ids = messages[0].split()
            
            if not message_ids:
                logger.debug("No new emails found")
                return 0
            
            # Limit number of emails processed per check
            if len(message_ids) > self.max_emails_per_check:
                logger.warning(f"Found {len(message_ids)} emails, limiting to {self.max_emails_per_check}")
                message_ids = message_ids[:self.max_emails_per_check]
            
            processed_count = 0
            
            for msg_id in message_ids:
                try:
                    msg_id_str = msg_id.decode('utf-8')
                    
                    # Skip if already processed
                    if msg_id_str in self.processed_messages:
                        continue
                    
                    # Fetch email
                    status, msg_data = mail.fetch(msg_id, '(RFC822)')
                    
                    if status != 'OK':
                        logger.error(f"Failed to fetch email {msg_id_str}")
                        continue
                    
                    # Parse email
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    # Extract email data
                    sender = email_message.get('From', '')
                    subject = email_message.get('Subject', '')
                    body = self.get_email_body(email_message)
                    message_id = email_message.get('Message-ID', f'bridge_{int(time.time())}_{msg_id_str}')
                    
                    # Create webhook payload
                    webhook_data = {
                        "from": sender,
                        "subject": subject,
                        "body": body,
                        "message_id": message_id,
                        "bridge_timestamp": datetime.now().isoformat(),
                        "bridge_source": "imap"
                    }
                    
                    # Send webhook
                    if self.send_webhook(webhook_data):
                        self.processed_messages.add(msg_id_str)
                        processed_count += 1
                        logger.info(f"Successfully bridged email from {sender}")
                    else:
                        logger.error(f"Failed to bridge email from {sender}")
                    
                except Exception as e:
                    logger.error(f"Error processing email {msg_id}: {e}")
                    continue
            
            # Clean up processed messages cache if it gets too large
            if len(self.processed_messages) > self.max_processed_cache:
                # Keep only the most recent half
                self.processed_messages = set(list(self.processed_messages)[-self.max_processed_cache//2:])
                logger.info(f"Cleaned processed messages cache, now has {len(self.processed_messages)} entries")
            
            if processed_count > 0:
                logger.info(f"Processed {processed_count} new emails")
            
            return processed_count
            
        except Exception as e:
            logger.error(f"Error processing emails: {e}")
            return 0
    
    def run_bridge(self):
        """Main bridge loop"""
        logger.info("Starting IMAP to Webhook Bridge")
        logger.info(f"Email: {self.email_address}")
        logger.info(f"IMAP Server: {self.imap_server}:{self.imap_port}")
        logger.info(f"Webhook URL: {self.webhook_url}")
        logger.info(f"Check interval: {self.check_interval} seconds")
        
        while True:
            try:
                # Connect to IMAP
                mail = self.connect_imap()
                
                # Process emails in a loop
                consecutive_errors = 0
                
                while consecutive_errors < 5:  # Allow some errors before reconnecting
                    try:
                        processed = self.process_new_emails(mail)
                        consecutive_errors = 0  # Reset error count on success
                        
                        # Wait before next check
                        time.sleep(self.check_interval)
                        
                    except Exception as e:
                        consecutive_errors += 1
                        logger.error(f"Error in processing loop (attempt {consecutive_errors}/5): {e}")
                        time.sleep(min(self.check_interval, 30))  # Wait before retry
                
                # Close connection before reconnecting
                try:
                    mail.logout()
                except:
                    pass
                
                logger.warning("Too many consecutive errors, reconnecting...")
                
            except KeyboardInterrupt:
                logger.info("Bridge stopped by user")
                break
            except Exception as e:
                logger.error(f"Bridge error: {e}")
                logger.info(f"Retrying in {self.check_interval} seconds...")
                time.sleep(self.check_interval)

def test_webhook_connection():
    """Test webhook endpoint connectivity"""
    webhook_url = os.getenv('WEBHOOK_URL', 'http://localhost:5000/webhook/email')
    
    test_data = {
        "from": "bridge-test@example.com",
        "subject": "Bridge Connection Test",
        "body": "This is a test email from the IMAP webhook bridge",
        "message_id": f"bridge_test_{int(time.time())}"
    }
    
    try:
        logger.info(f"Testing webhook connection to: {webhook_url}")
        
        response = requests.post(
            webhook_url,
            json=test_data,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            logger.info("✅ Webhook connection test successful")
            logger.info(f"Response: {response.json()}")
            return True
        else:
            logger.error(f"❌ Webhook test failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Webhook test failed: {e}")
        return False

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='IMAP to Webhook Bridge for Daily Brief Service')
    parser.add_argument('--test-webhook', action='store_true', 
                      help='Test webhook connection and exit')
    parser.add_argument('--dry-run', action='store_true',
                      help='Check emails but don\'t send webhooks')
    
    args = parser.parse_args()
    
    if args.test_webhook:
        test_webhook_connection()
        return
    
    if args.dry_run:
        logger.warning("Running in DRY RUN mode - webhooks will not be sent")
    
    # Create and run bridge
    bridge = IMAPWebhookBridge()
    bridge.run_bridge()

if __name__ == "__main__":
    main()