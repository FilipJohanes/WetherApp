#!/usr/bin/env python3
"""
Daily Brief Service - Webhook Version
Email-driven weather subscriptions and calendar reminders via API webhooks.

This version receives email notifications via webhooks instead of polling IMAP.
Much more efficient and scalable than the polling approach.
"""

import os
import json
import sqlite3
import logging
import hashlib
import re
import base64
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr
from typing import Dict, List, Optional, NamedTuple
from zoneinfo import ZoneInfo
import requests
import dateparser
from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# Import existing functions from the original app
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import (
    Config, EmailMessageInfo, load_env, process_inbound_email,
    run_daily_weather_job, run_due_reminders_job, should_process_email
)

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

app = Flask(__name__)
scheduler = BackgroundScheduler()

# Global services - initialized in main()
config = None
db_helper = None
weather_service = None
geocoding_service = None
subscriber_service = None
reminder_service = None
notification_service = None
email_parser = None

class WebhookEmailData(NamedTuple):
    """Represents email data from webhook"""
    sender: str
    subject: str
    body: str
    timestamp: datetime
    message_id: str

def parse_gmail_webhook(webhook_data: dict) -> Optional[WebhookEmailData]:
    """Parse Gmail webhook notification data"""
    try:
        # Gmail Pub/Sub webhook format
        if 'message' in webhook_data:
            message = webhook_data['message']
            if 'data' in message:
                # Decode base64 data
                decoded_data = base64.b64decode(message['data']).decode('utf-8')
                email_data = json.loads(decoded_data)
                
                return WebhookEmailData(
                    sender=email_data.get('from', ''),
                    subject=email_data.get('subject', ''),
                    body=email_data.get('body', ''),
                    timestamp=datetime.now(ZoneInfo('UTC')),
                    message_id=email_data.get('message_id', '')
                )
    except Exception as e:
        logger.error(f"Error parsing Gmail webhook data: {e}")
        return None

def parse_generic_webhook(webhook_data: dict) -> Optional[WebhookEmailData]:
    """Parse generic email webhook data"""
    try:
        return WebhookEmailData(
            sender=webhook_data.get('from', ''),
            subject=webhook_data.get('subject', ''),
            body=webhook_data.get('body', ''),
            timestamp=datetime.now(ZoneInfo('UTC')),
            message_id=webhook_data.get('message_id', str(hash(webhook_data.get('subject', '') + webhook_data.get('from', ''))))
        )
    except Exception as e:
        logger.error(f"Error parsing generic webhook data: {e}")
        return None

def process_webhook_email(email_data: WebhookEmailData, dry_run: bool = False) -> Dict:
    """Process email received via webhook"""
    try:
        logger.info(f"Processing webhook email from {email_data.sender}")
        
        # Check if we should process this email (same filtering as before)
        if not should_process_email(email_data.sender, email_data.subject, email_data.body):
            logger.info(f"Skipping email from {email_data.sender} - filtered out")
            return {"status": "filtered", "reason": "Email filtered by processing rules"}
        
        # Check for duplicates using the same inbox_log mechanism
        email_hash = hashlib.md5(f"{email_data.sender}{email_data.subject}{email_data.body}".encode()).hexdigest()
        
        with db_helper.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM inbox_log WHERE email_hash = ?",
                (email_hash,)
            )
            if cursor.fetchone()[0] > 0:
                logger.info(f"Email already processed: {email_hash}")
                return {"status": "duplicate", "reason": "Email already processed"}
            
            # Log this email
            cursor.execute(
                "INSERT INTO inbox_log (email_hash, sender, subject, processed_at) VALUES (?, ?, ?, ?)",
                (email_hash, email_data.sender, email_data.subject, email_data.timestamp)
            )
        
        # Parse and process the email command
        command = email_parser.parse_email_command(
            email_data.sender, email_data.subject, email_data.body
        )
        
        if command.command_type == 'weather_subscription':
            result = subscriber_service.handle_subscription_command(command, dry_run)
        elif command.command_type == 'calendar_reminder':
            result = reminder_service.handle_reminder_command(command, dry_run)
        elif command.command_type == 'unsubscribe':
            result = subscriber_service.handle_unsubscribe_command(command, dry_run)
        else:
            result = {"status": "error", "message": "Unknown command type"}
        
        logger.info(f"Webhook email processed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error processing webhook email: {e}")
        return {"status": "error", "message": str(e)}

@app.route('/webhook/email', methods=['POST'])
def webhook_email():
    """Handle incoming email webhooks"""
    try:
        webhook_data = request.get_json()
        if not webhook_data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        logger.info(f"Received webhook: {json.dumps(webhook_data, indent=2)}")
        
        # Try to parse different webhook formats
        email_data = None
        
        # Gmail Pub/Sub format
        if 'message' in webhook_data:
            email_data = parse_gmail_webhook(webhook_data)
        else:
            # Generic format
            email_data = parse_generic_webhook(webhook_data)
        
        if not email_data:
            return jsonify({"error": "Could not parse email data"}), 400
        
        # Process the email
        result = process_webhook_email(email_data, dry_run=False)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/webhook/test', methods=['POST'])
def webhook_test():
    """Test endpoint for webhook functionality"""
    test_email = {
        "from": "test@example.com",
        "subject": "Prague, Czech Republic",
        "body": "I would like to subscribe to weather updates for Prague.",
        "message_id": "test_" + str(int(datetime.now().timestamp()))
    }
    
    email_data = parse_generic_webhook(test_email)
    result = process_webhook_email(email_data, dry_run=True)
    
    return jsonify({"test_data": test_email, "result": result}), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Daily Brief Webhook Service"
    }), 200

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get service statistics"""
    try:
        with db_helper.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get subscriber count
            cursor.execute("SELECT COUNT(*) FROM subscribers WHERE active = 1")
            active_subscribers = cursor.fetchone()[0]
            
            # Get reminder count
            cursor.execute("SELECT COUNT(*) FROM reminders WHERE sent = 0")
            pending_reminders = cursor.fetchone()[0]
            
            # Get processed email count (last 24h)
            yesterday = datetime.now() - timedelta(days=1)
            cursor.execute("SELECT COUNT(*) FROM inbox_log WHERE processed_at > ?", (yesterday,))
            recent_emails = cursor.fetchone()[0]
        
        return jsonify({
            "active_subscribers": active_subscribers,
            "pending_reminders": pending_reminders,
            "emails_processed_24h": recent_emails,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({"error": str(e)}), 500

def run_daily_weather_job_webhook(dry_run: bool = False):
    """Send daily weather forecasts (scheduled job)"""
    try:
        logger.info("Starting daily weather job (webhook version)")
        
        with db_helper.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT email, location, timezone, language, personality 
                FROM subscribers 
                WHERE active = 1
            """)
            
            for row in cursor.fetchall():
                email, location, timezone, language, personality = row
                try:
                    weather_data = weather_service.get_weather_forecast(location)
                    if weather_data:
                        message = weather_service.format_weather_message(
                            weather_data, language, personality
                        )
                        
                        if not dry_run:
                            notification_service.send_weather_email(
                                email, location, message, language
                            )
                        else:
                            logger.info(f"DRY RUN: Would send weather to {email}")
                        
                        logger.info(f"Daily weather sent to {email}")
                    
                except Exception as e:
                    logger.error(f"Error sending weather to {email}: {e}")
        
        logger.info("Daily weather job completed")
        
    except Exception as e:
        logger.error(f"Daily weather job error: {e}")

def run_due_reminders_job_webhook(dry_run: bool = False):
    """Send due calendar reminders (scheduled job)"""
    try:
        logger.info("Checking for due reminders (webhook version)")
        
        with db_helper.get_connection() as conn:
            cursor = conn.cursor()
            current_time = datetime.now()
            
            cursor.execute("""
                SELECT id, email, message, reminder_time, language
                FROM reminders 
                WHERE sent = 0 AND reminder_time <= ?
                ORDER BY reminder_time
            """, (current_time,))
            
            for row in cursor.fetchall():
                reminder_id, email, message, reminder_time, language = row
                try:
                    if not dry_run:
                        notification_service.send_reminder_email(
                            email, message, reminder_time, language
                        )
                        
                        cursor.execute(
                            "UPDATE reminders SET sent = 1, sent_at = ? WHERE id = ?",
                            (current_time, reminder_id)
                        )
                    else:
                        logger.info(f"DRY RUN: Would send reminder to {email}")
                    
                    logger.info(f"Reminder sent to {email}: {message}")
                    
                except Exception as e:
                    logger.error(f"Error sending reminder {reminder_id}: {e}")
        
        logger.info("Due reminders job completed")
        
    except Exception as e:
        logger.error(f"Due reminders job error: {e}")

def main():
    """Initialize and start the webhook service"""
    global config, db_helper, weather_service, geocoding_service
    global subscriber_service, reminder_service, notification_service, email_parser
    
    # Initialize configuration
    config = Config()
    
    # Initialize services
    db_helper = DatabaseHelper(config.db_path)
    weather_service = WeatherService()
    geocoding_service = GeocodingService()
    subscriber_service = SubscriberService(db_helper, weather_service, geocoding_service, notification_service)
    reminder_service = ReminderService(db_helper, notification_service)
    notification_service = NotificationService(config)
    email_parser = EmailParser()
    
    # Initialize database
    db_helper.init_database()
    
    # Set up background scheduler for timed jobs
    scheduler.add_job(
        func=lambda: run_daily_weather_job_webhook(False),
        trigger=CronTrigger(hour=5, minute=0),
        id='daily_weather_webhook',
        name='Send daily weather forecasts (webhook version)'
    )
    
    scheduler.add_job(
        func=lambda: run_due_reminders_job_webhook(False),
        trigger=CronTrigger(minute='*/1'),  # Every minute
        id='check_reminders_webhook', 
        name='Send due calendar reminders (webhook version)'
    )
    
    scheduler.start()
    
    logger.info("Daily Brief Webhook Service initialized")
    logger.info("Webhook endpoint: /webhook/email")
    logger.info("Test endpoint: /webhook/test")
    logger.info("Health check: /health")
    logger.info("Stats: /stats")
    
    # Get port from environment or use default
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    
    logger.info(f"Starting webhook server on {host}:{port}")
    
    try:
        app.run(host=host, port=port, debug=False)
    except KeyboardInterrupt:
        logger.info("Shutting down webhook service")
        scheduler.shutdown()

if __name__ == "__main__":
    main()