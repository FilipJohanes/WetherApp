# 📁 Examples & Development Files

This directory contains example configurations, development utilities, and sample email senders:

## Configuration Examples
- `.env.example` - Sample environment configuration
- `.env.bridge-example` - Sample webhook bridge configuration  
- `requirements-dev.txt` - Development dependencies

## Email Testing Examples 📧
- `send_hybrid_weather.py` - Complete localized weather emails (uses weather_messages.txt + localization)
- `send_localized_weather.py` - Basic localized weather emails
- `send_test_email.py` - Simple weather email sender
- `send_weather_now.py` - Immediate weather email with basic formatting

## Development Data
- `weather_messages.txt` - Sample weather message outputs
- `development_examples.py` - Code examples and snippets

## Usage
```bash
# Copy example configuration
cp .env.example ../.env
# Edit with your credentials

# Install dev dependencies  
pip install -r requirements-dev.txt

# Test localized emails (only sends to your email)
python send_hybrid_weather.py
```

**⚠️ Note:** All email examples are configured to only send to `filip.johanes9@gmail.com` to avoid spam!