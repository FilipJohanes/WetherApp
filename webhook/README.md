# 📁 Webhook Components

This directory contains the webhook-based architecture for scalable email processing:

- `webhook_simple.py` - Basic Flask webhook server  
- `webhook_app.py` - Advanced webhook with full features
- `imap_webhook_bridge.py` - Bridge to convert IMAP to webhooks
- `requirements-webhook.txt` - Webhook-specific dependencies

## Usage
```bash
# Start webhook server
python webhook_simple.py

# Start IMAP bridge (in separate terminal)  
python imap_webhook_bridge.py
```

See `/docs/WEBHOOK_GUIDE.md` for detailed instructions.