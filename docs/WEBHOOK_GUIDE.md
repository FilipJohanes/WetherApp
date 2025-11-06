# Daily Brief Service - Webhook Integration Guide

## Overview

This guide shows how to convert your Daily Brief Service from polling-based email checking to event-driven webhook processing. This is much more efficient and scalable.

## Webhook Architecture

### Before (Polling):
```
[Service] --check every 1min--> [IMAP Server] --fetch emails--> [Process]
```

### After (Webhooks):
```
[Email Provider] --instant webhook--> [Your Service] --process immediately--> [Response]
```

## Benefits

1. **Instant Processing**: Emails are processed immediately when they arrive
2. **Better Scalability**: No polling overhead, handles thousands of emails efficiently  
3. **Resource Efficient**: No constant IMAP connections or polling
4. **Reliable**: No missed emails due to polling intervals

## Setup Options

### Option 1: Gmail with Pub/Sub (Recommended for Gmail)

1. **Enable Gmail API**:
   - Go to Google Cloud Console
   - Enable Gmail API for your project
   - Create service account credentials

2. **Set up Pub/Sub Topic**:
   ```bash
   # Create topic
   gcloud pubsub topics create gmail-notifications
   
   # Create subscription
   gcloud pubsub subscriptions create gmail-webhook-sub --topic=gmail-notifications
   ```

3. **Configure Gmail Watch**:
   ```python
   # gmail_webhook_setup.py
   from google.oauth2.service_account import Credentials
   from googleapiclient.discovery import build

   def setup_gmail_webhook():
       credentials = Credentials.from_service_account_file('path/to/service-account.json')
       service = build('gmail', 'v1', credentials=credentials)
       
       request = {
           'labelIds': ['INBOX'],
           'topicName': 'projects/your-project/topics/gmail-notifications'
       }
       
       result = service.users().watch(userId='me', body=request).execute()
       print(f"Watch set up: {result}")
   ```

### Option 2: Email Forwarding with Zapier/IFTTT

1. **Create Zapier Webhook**:
   - Trigger: Gmail - New Email
   - Action: Webhooks - POST to your service

2. **IFTTT Alternative**:
   - If: Gmail - Any new email in inbox
   - Then: Webhooks - Make web request

### Option 3: Email Parsing Services

Use services like:
- **SendGrid Inbound Parse**
- **Mailgun Routes** 
- **Postmark Inbound**

### Option 4: Custom IMAP Webhook Bridge

For any email provider, create a lightweight bridge:

```python
# imap_webhook_bridge.py
import imaplib
import requests
import time
import json
from email import message_from_bytes

def imap_to_webhook_bridge():
    # Connect to IMAP
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login('your-email@gmail.com', 'your-password')
    mail.select('inbox')
    
    processed_messages = set()
    
    while True:
        # Check for new messages
        status, messages = mail.search(None, 'UNSEEN')
        
        for msg_id in messages[0].split():
            if msg_id in processed_messages:
                continue
                
            # Fetch message
            status, msg_data = mail.fetch(msg_id, '(RFC822)')
            email_body = msg_data[0][1]
            email_message = message_from_bytes(email_body)
            
            # Extract email data
            webhook_data = {
                "from": email_message['From'],
                "subject": email_message['Subject'],
                "body": get_email_body(email_message),
                "message_id": email_message['Message-ID']
            }
            
            # Send to webhook
            try:
                response = requests.post(
                    'http://localhost:5000/webhook/email',
                    json=webhook_data,
                    timeout=10
                )
                if response.status_code == 200:
                    processed_messages.add(msg_id)
                    print(f"Processed email: {email_message['Subject']}")
            except Exception as e:
                print(f"Webhook error: {e}")
        
        time.sleep(5)  # Check every 5 seconds instead of 1 minute
```

## Running the Webhook Service

### 1. Install Dependencies

```bash
pip install -r requirements-webhook.txt
```

### 2. Start the Service

```bash
python webhook_app.py
```

The service will start on `http://localhost:5000` with these endpoints:

- `POST /webhook/email` - Main webhook endpoint
- `POST /webhook/test` - Test endpoint  
- `GET /health` - Health check
- `GET /stats` - Service statistics

### 3. Test the Webhook

```bash
# Test with curl
curl -X POST http://localhost:5000/webhook/test

# Test with real data
curl -X POST http://localhost:5000/webhook/email \
  -H "Content-Type: application/json" \
  -d '{
    "from": "user@example.com",
    "subject": "Prague, Czech Republic", 
    "body": "Subscribe me to weather updates",
    "message_id": "test123"
  }'
```

## Webhook Data Format

### Generic Format (Most Services):
```json
{
  "from": "user@example.com",
  "subject": "Prague, Czech Republic",
  "body": "Email content here",
  "message_id": "unique-message-id"
}
```

### Gmail Pub/Sub Format:
```json
{
  "message": {
    "data": "base64-encoded-json-data",
    "messageId": "message-id",
    "publishTime": "2024-01-01T12:00:00Z"
  }
}
```

## Production Deployment

### 1. Environment Variables

```bash
# .env file
HOST=0.0.0.0
PORT=5000
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
# ... other existing vars
```

### 2. Deploy Options

**Docker**:
```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements-webhook.txt
EXPOSE 5000
CMD ["python", "webhook_app.py"]
```

**Railway/Heroku**:
- Push code to Git
- Set environment variables
- Deploy automatically

**VPS/Cloud**:
```bash
# Install dependencies
pip install -r requirements-webhook.txt

# Run with gunicorn for production
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 webhook_app:app
```

### 3. Reverse Proxy (nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Migration Strategy

### Phase 1: Parallel Testing
1. Keep existing polling service running
2. Deploy webhook service on different port
3. Set up webhook integration
4. Compare results for a few days

### Phase 2: Switch Over  
1. Stop polling service
2. Switch to webhook service
3. Monitor for issues

### Phase 3: Cleanup
1. Remove polling-related code
2. Update documentation
3. Optimize webhook service

## Monitoring & Debugging

### Logs
The webhook service logs all incoming requests:

```
2024-01-01 12:00:00 - INFO - Received webhook: {"from": "user@example.com", ...}
2024-01-01 12:00:01 - INFO - Processing webhook email from user@example.com
2024-01-01 12:00:02 - INFO - Webhook email processed: {"status": "success"}
```

### Webhook Testing Tools
- **ngrok**: Expose local service to internet for testing
- **Postman**: Test webhook endpoints
- **curl**: Command-line testing

### Health Monitoring
```bash
# Check if service is running
curl http://localhost:5000/health

# Get service statistics
curl http://localhost:5000/stats
```

## Security Considerations

1. **Authentication**: Add webhook signature verification
2. **Rate Limiting**: Prevent spam/DoS attacks
3. **Input Validation**: Sanitize all webhook data
4. **HTTPS**: Use SSL/TLS in production
5. **Firewall**: Restrict access to webhook endpoints

## Performance Benefits

- **Latency**: ~1-60 seconds (polling) → ~1-5 seconds (webhook)
- **Resource Usage**: ~50MB RAM constant → ~10MB RAM base + spikes
- **Network**: Constant IMAP connections → Event-driven requests
- **Scalability**: Limited by polling frequency → Limited by server capacity

This webhook approach will handle thousands of emails much better than the current polling system!