#!/usr/bin/env python3
"""
Daily Brief Service - Simplified Webhook Version
Email-driven weather subscriptions and calendar reminders via API webhooks.

This version receives email notifications via webhooks instead of polling IMAP.
Works with your existing app.py function-based structure.
"""

import os
import json
import logging
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, NamedTuple
from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# Import existing functions from the original app
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
logger = logging.getLogger(__name__)

app = Flask(__name__)
scheduler = BackgroundScheduler()

# Global config - initialized in main()
config = None

class WebhookEmailData(NamedTuple):
    """Represents email data from webhook"""
    sender: str
    subject: str
    body: str
    timestamp: datetime
    message_id: str

def webhook_to_email_info(webhook_data: WebhookEmailData) -> EmailMessageInfo:
    """Convert webhook data to EmailMessageInfo format"""
    return EmailMessageInfo(
        sender=webhook_data.sender,
        subject=webhook_data.subject,
        body=webhook_data.body,
        timestamp=webhook_data.timestamp,
        uid=webhook_data.message_id  # Use message_id as uid
    )

def parse_webhook_data(webhook_data: dict) -> Optional[WebhookEmailData]:
    """Parse webhook data into standard format"""
    try:
        return WebhookEmailData(
            sender=webhook_data.get('from', ''),
            subject=webhook_data.get('subject', ''),
            body=webhook_data.get('body', ''),
            timestamp=datetime.now(),
            message_id=webhook_data.get('message_id', str(hash(webhook_data.get('subject', '') + webhook_data.get('from', ''))))
        )
    except Exception as e:
        logger.error(f"Error parsing webhook data: {e}")
        return None

def check_duplicate_email(sender: str, subject: str, body: str) -> bool:
    """Check if this email was already processed"""
    try:
        import sqlite3
        email_hash = hashlib.md5(f"{sender}{subject}{body}".encode()).hexdigest()
        
        with sqlite3.connect(config.db_path) as conn:
            cursor = conn.cursor()
            
            # Create inbox_log table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS inbox_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email_hash TEXT UNIQUE,
                    sender TEXT,
                    subject TEXT,
                    processed_at TIMESTAMP
                )
            ''')
            
            cursor.execute(
                "SELECT COUNT(*) FROM inbox_log WHERE email_hash = ?",
                (email_hash,)
            )
            
            if cursor.fetchone()[0] > 0:
                logger.info(f"Email already processed: {email_hash}")
                return True
            
            # Log this email
            cursor.execute(
                "INSERT INTO inbox_log (email_hash, sender, subject, processed_at) VALUES (?, ?, ?, ?)",
                (email_hash, sender, subject, datetime.now())
            )
            
        return False
        
    except Exception as e:
        logger.error(f"Error checking duplicate email: {e}")
        return False

def process_webhook_email(email_data: WebhookEmailData, dry_run: bool = False) -> Dict:
    """Process email received via webhook"""
    try:
        logger.info(f"Processing webhook email from {email_data.sender}")
        
        # Check if we should process this email
        if not should_process_email(email_data.sender, email_data.subject, email_data.body):
            logger.info(f"Skipping email from {email_data.sender} - filtered out")
            return {"status": "filtered", "reason": "Email filtered by processing rules"}
        
        # Check for duplicates
        if check_duplicate_email(email_data.sender, email_data.subject, email_data.body):
            return {"status": "duplicate", "reason": "Email already processed"}
        
        # Convert to EmailMessageInfo and process using existing function
        msg_info = webhook_to_email_info(email_data)
        
        # Use the existing process_inbound_email function
        process_inbound_email(config, msg_info, dry_run)
        
        logger.info(f"Webhook email processed successfully")
        return {"status": "success", "message": "Email processed"}
        
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
        
        logger.info(f"Received webhook from: {webhook_data.get('from', 'unknown')}")
        
        # Parse email data
        email_data = parse_webhook_data(webhook_data)
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
    
    logger.info("Running webhook test with sample data")
    email_data = parse_webhook_data(test_email)
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
        import sqlite3
        with sqlite3.connect(config.db_path) as conn:
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

def main():
    """Initialize and start the webhook service"""
    global config
    
    # Initialize configuration using existing load_env function
    config = load_env()
    
    # Set up background scheduler for timed jobs (same as original app)
    scheduler.add_job(
        func=lambda: run_daily_weather_job(config, False),
        trigger=CronTrigger(hour=5, minute=0),
        id='daily_weather_webhook',
        name='Send daily weather forecasts (webhook version)'
    )
    
    scheduler.add_job(
        func=lambda: run_due_reminders_job(config, False),
        trigger=CronTrigger(minute='*/1'),  # Every minute
        id='check_reminders_webhook', 
        name='Send due calendar reminders (webhook version)'
    )
    
    scheduler.start()
    
    logger.info("Daily Brief Webhook Service initialized")
    logger.info("Configuration loaded successfully")
    logger.info("Webhook endpoint: POST /webhook/email")
    logger.info("Test endpoint: POST /webhook/test")
    logger.info("Health check: GET /health")
    logger.info("Stats: GET /stats")
    
    # Get port from environment or use default
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '127.0.0.1')  # Use localhost for testing
    
    logger.info(f"Starting webhook server on {host}:{port}")
    
    try:
        app.run(host=host, port=port, debug=True, use_reloader=False)
    except KeyboardInterrupt:
        logger.info("Shutting down webhook service")
        scheduler.shutdown()

if __name__ == "__main__":
    main()