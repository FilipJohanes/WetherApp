# 📬 Daily Brief Service

![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)
![License](https://img.shields.io/badge/license-Proprietary-red.svg)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20macos-lightgrey.svg)
![Tests](https://img.shields.io/badge/tests-17%2F17%20passed-brightgreen.svg)
![Languages](https://img.shields.io/badge/languages-EN%20%7C%20ES%20%7C%20SK-blue.svg)

> 🚀 **Proprietary multi-language email-driven weather service**  
> **© 2025 Filip Johanes. All Rights Reserved.**

⚠️ **PROPRIETARY SOFTWARE** - This project contains proprietary algorithms and unique features. Commercial use, redistribution, or derivative works are strictly prohibited. See [LICENSE](LICENSE) for details.

A comprehensive Python 3.11+ service that transforms your email inbox into a smart weather assistant with full multi-language support:

1. **🌤️ Daily Weather Digest** - Subscribe by sending your location, receive personalized forecasts at 05:00
2. **🎭 Multi-Language Personality Modes** - Choose from 3 personalities (neutral, cute, brutal) in 3 languages (English, Spanish, Slovak)
3. **🛡️ Smart Email Processing** - Handles system emails, Unicode characters, and flexible input parsing

## ✨ Features

- **🆓 100% Free**: Uses Open-Meteo weather API (no API keys required)
- **📧 Email-Driven**: Control everything via simple email commands  
- **🌍 Multi-Language**: Full support for English, Spanish, and Slovak
- **🎭 3 Personality Modes**: Neutral, cute, brutal communication styles
- **🧠 Smart Parsing**: Handles multi-line emails, system email filtering, Unicode support
- **🛡️ Production Ready**: Handles duplicates, restarts, network failures, and crashes gracefully
- **📦 Self-Contained**: Organized structure with comprehensive documentation
- **⏰ Timezone Aware**: Configurable timezone support (default: Europe/Bratislava)
- **🔄 Cross-Platform**: Works on Windows, Linux, macOS, and Raspberry Pi
- **🔧 Webhook Ready**: Scalable architecture with Flask webhook support available

## 📁 Project Structure

```
📁 reminderAPP/
├── 📄 app.py                    # ⚡ Main service application
├── 📄 .env                      # 🔐 Configuration (email credentials)  
├── 📄 requirements.txt          # 📦 Core dependencies
├── 📄 README.md                # 📖 This file
│
├── 📁 docs/                     # 📚 Documentation & guides
│   ├── DEPLOYMENT.md            # � Production setup guide
│   ├── WEBHOOK_GUIDE.md         # 🔗 Webhook architecture docs
│   └── 📁 user-guides/         # 👤 User manuals & quick reference
│
├── 📁 languages/               # 🌍 Multi-language support  
│   ├── 📁 en/es/sk/            # English, Spanish, Slovak messages
│
├── 📁 tests/                   # 🧪 Comprehensive test suite (14 test files)
│   └── test_*.py               # All functionality tests
│
├── 📁 scripts/                 # 🛠️ Utilities & deployment tools
│   ├── check_db.py             # Database inspection
│   └── 📁 deployment/          # Automated deployment scripts  
│
├── 📁 webhook/                 # � Scalable webhook architecture
│   ├── webhook_simple.py       # Basic Flask webhook server
│   └── imap_webhook_bridge.py  # IMAP to webhook bridge
│
└── 📁 examples/                # 📋 Sample configs & development files
│   └── 📁 debug/               # Debug & maintenance tools
│
└── 📁 examples/                # Sample configurations
```

## 📖 Table of Contents

- [🚀 Quick Start](#-quick-start)
- [📚 Documentation](#-documentation) 
- [📧 Usage Guide](#-usage-guide)
- [🎭 Personality Modes](#-personality-modes)
- [🌍 Language Support](#-language-support)
- [🛠️ CLI Commands](#️-cli-commands)
- [📊 Example Responses](#-example-responses)
- [🏗️ Architecture](#️-architecture)
- [🔧 Configuration](#-configuration)
- [🧪 Testing](#-testing)
- [🚀 Deployment](#-deployment)
- [🚨 Troubleshooting](#-troubleshooting)
- [🤝 Contributing](#-contributing)
- [📝 License](#-license)

## 📚 Documentation

Your complete guide to using and deploying the Daily Brief Service:

### 👥 **For Users & Alpha Testers:**
- **[📖 User Manual](docs/user-guides/USER_MANUAL.md)** - Complete guide with examples
- **[⚡ Quick Reference](docs/user-guides/QUICK_REFERENCE.md)** - Cheat sheet for commands
- **[📧 Welcome Template](docs/user-guides/WELCOME_EMAIL_TEMPLATE.md)** - Auto-response content

### 🛠️ **For Deployment & Setup:**
- **[✅ Final Checklist](docs/deployment/FINAL_CHECKLIST.md)** - Pre-deployment verification
- **[💻 Local PC Setup](docs/deployment/DEPLOY_LOCAL_PC.md)** - Windows/Mac/Linux deployment
- **[🥧 Raspberry Pi Guide](docs/deployment/DEPLOY_PI_ZERO_2W.md)** - Pi Zero 2 W specific setup
- **[☁️ Cloud Options](docs/deployment/DEPLOY_CLOUD_OPTIONS.md)** - AWS/Azure/VPS deployment
- **[📧 Email Configuration](docs/deployment/EMAIL_SETUP_GUIDE.md)** - Gmail & other providers
- **[🚀 Alpha Testing Ready](docs/deployment/ALPHA_DEPLOYMENT_READY.md)** - Readiness assessment

### 🔧 **Project Structure:**
- **[📁 Structure Guide](PROJECT_STRUCTURE.md)** - Detailed directory organization

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/daily-brief-service.git
cd daily-brief-service
```

### 2. Install Dependencies

```bash
# Using pip
pip install -r requirements.txt

# Or using virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Email Settings

Copy the example environment file and configure your email settings:

```bash
# Copy example configuration
cp .env.example .env

# Edit with your email provider details
nano .env  # or use your preferred editor
```

Required environment variables:

```bash
# Required Settings
EMAIL_ADDRESS="your-service-email@example.com"
EMAIL_PASSWORD="your-app-password"      # Use app password for Gmail
IMAP_HOST="imap.gmail.com"              # Your IMAP server
SMTP_HOST="smtp.gmail.com"              # Your SMTP server

# Optional Settings (with defaults)
IMAP_PORT="993"
SMTP_PORT="587" 
SMTP_USE_TLS="true"
TZ="Europe/Bratislava"
LANGUAGE="en"                           # Default language (en/es/sk)
```

#### Email Provider Examples:

**Gmail:**
```bash
export IMAP_HOST="imap.gmail.com"
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USE_TLS="true"
```

**Outlook/Hotmail:**
```bash
export IMAP_HOST="outlook.office365.com"
export SMTP_HOST="smtp.office365.com"
export SMTP_PORT="587"
export SMTP_USE_TLS="true"
```

### 4. Test Configuration

```bash
# Test your email setup
python app.py --send-test your-email@example.com

# Run in dry-run mode (no emails sent)
python app.py --dry-run
```

### 5. Run the Service

```bash
python app.py
```

The service will automatically:
- ✅ Create `app.db` SQLite database
- 🔄 Check for emails every minute  
- 🌅 Send daily weather at 05:00 local time
- ⏰ Process calendar reminders on schedule
- 📝 Log all activities to `app.log`

## 📧 Usage Guide

Send emails to your configured service address with these commands:

### Weather Subscriptions

**Subscribe to daily weather:**
```
Bratislava
```
or
```
Prague, Czech Republic
```
or coordinates:
```
40.7128,-74.0060
```

**Unsubscribe:**
```
delete
```

### Personality Modes 🎭

Choose how you want your weather reports delivered:

**Neutral mode (default):**
```
neutral
```

**Cute mode (friendly with emojis):**
```
cute
```

**Brutal mode (blunt and direct):**
```
brutal
```

**Set personality during subscription:**
```
Prague, Czech Republic
personality=cute
```

**Set language and personality:**
```
Madrid, Spain
personality=brutal
language=es
```

### 🌍 Multi-Language Support

The service supports multiple languages for weather messages:

**English (en)** - Default language with full personality support
**Spanish (es)** - Complete translations for all personality modes
**Slovak (sk)** - Complete Slovak language support with all personality modes

**Language Examples:**
```
# English weather (default)
London
personality=cute

# Spanish weather  
Madrid
personality=brutal
language=es

# Slovak weather
Bratislava
personality=neutral
language=sk
```

### Calendar Reminders

**Schedule a reminder:**
```
date=2025-12-01
time=08:30
message=Doctor Appointment
repeat=3
```

**Field details:**
- `date=` - Any format: `tomorrow`, `2025-12-01`, `next Friday`
- `time=` - Any format: `08:30`, `8am`, `noon`, `2:30 PM`
- `message=` - Your reminder text (required)
- `repeat=` - Number of reminders (optional, default 1)

Repeats are sent every 10 minutes after the first reminder.

**Delete all reminders:**
```
delete
```

## 🛠️ CLI Commands

```bash
# List current weather subscribers
python app.py --list-subs

# List pending calendar reminders  
python app.py --list-reminders

# Send test email to verify setup
python app.py --send-test user@example.com

# Run without sending emails (testing)
python app.py --dry-run
```

## 📊 Example Responses

### Weather Subscription Confirmation
```
✅ Weather subscription updated!
📍 Location: Bratislava, Slovakia (48.1482, 17.1067)

Here's today's forecast:
Today's weather for Bratislava, Slovakia:

🌡️ Temperature: High 22°C / Low 13°C
🌧️ Rain probability: 60% (≈4.2 mm)
💨 Wind: up to 25 km/h

👕 Clothing recommendation: Light jacket or sweater, rain jacket, waterproof shoes
```

### Personality Mode Examples

**Neutral Mode:**
```
💡 Take an umbrella - it's going to rain today.
👕 Clothing recommendation: light jacket or sweater, rain jacket, waterproof shoes
```

**Cute Mode:**
```
💡 🌧️ Pitter-patter raindrops are coming! Don't forget your cute umbrella! ☂️
👕 Fashion advice: Wear light jacket or sweater, rain jacket, waterproof shoes and look absolutely adorable! 💖
```

**Brutal Mode:**
```
💡 Rain incoming. Umbrella or get soaked. Your choice.
🥶 Survival gear: light jacket or sweater, rain jacket, waterproof shoes or suffer the consequences.
```

### Calendar Reminder Confirmation
```
✅ Calendar reminder scheduled!

📝 Message: Doctor Appointment
📅 First reminder: 2025-12-01 08:30 CET
🔄 Total reminders: 3 (every 10 minutes)
📅 Last reminder: 2025-12-01 08:50 CET

💡 To delete all your pending reminders, just reply with 'delete'.
```

## 🧪 Testing

Run the comprehensive test suite to verify all functionality:

### **Quick Test:**
```bash
# Run all tests (17 tests, 100% pass rate)
cd testing
python test_all.py
```

### **Specific Tests:**
```bash
# Multi-language tests
python test_multilang.py

# Slovak language tests
python test_slovak_complete.py

# Message system validation
python test_messages_comprehensive.py

# Integration testing
python test_integration_sk.py
```

### **Debug Tools:**
```bash
# Check service status
cd scripts/debug
python check_status.py

# Test personality modes
python debug_personality.py

# Database management tools
python db_manager.py
```

**Test Coverage:**
- ✅ Multi-language support (EN/ES/SK)
- ✅ All personality modes (neutral/cute/brutal)
- ✅ Weather message generation
- ✅ Email parsing and validation
- ✅ Database operations
- ✅ Slovak language implementation
- ✅ Integration scenarios

---

## 🚀 Deployment

Choose your deployment platform with automated setup scripts:

### **🖥️ Local PC (Windows/Mac/Linux)**
```bash
# Quick deployment
scripts/deployment/quick_deploy.bat    # Windows
./scripts/deployment/quick_deploy.sh   # Linux/Mac
```
📖 **[Complete Local Setup Guide](docs/deployment/DEPLOY_LOCAL_PC.md)**

### **🥧 Raspberry Pi Zero 2 W**
```bash
# Automated Pi setup
./scripts/deployment/setup_pi_zero.sh
```
📖 **[Pi Zero 2 W Setup Guide](docs/deployment/DEPLOY_PI_ZERO_2W.md)**

### **☁️ Cloud Deployment**
- **AWS EC2**: Free tier compatible
- **Azure VM**: Student credits supported
- **Google Cloud**: Compute Engine
- **VPS Providers**: DigitalOcean, Linode, Vultr

📖 **[Cloud Options Guide](docs/deployment/DEPLOY_CLOUD_OPTIONS.md)**

### **📧 Email Configuration**
Supports Gmail, Outlook, Yahoo, and custom SMTP/IMAP:

```bash
# Copy example config
cp .env.example .env

# Edit with your credentials
# See EMAIL_SETUP_GUIDE.md for provider-specific instructions
```

📖 **[Email Setup Guide](docs/deployment/EMAIL_SETUP_GUIDE.md)**
📖 **[Quick Email Setup](docs/deployment/QUICK_EMAIL_SETUP.md)**

### **✅ Pre-Deployment Checklist**
📖 **[Final Checklist](docs/deployment/FINAL_CHECKLIST.md)** - Verify readiness before going live

---

## 🏗️ Architecture

### Database Schema

**subscribers** - Weather service users
```sql
CREATE TABLE subscribers (
    email TEXT PRIMARY KEY,
    location TEXT NOT NULL,
    lat REAL NULL,
    lon REAL NULL, 
    updated_at TEXT NOT NULL
);
```

**reminders** - Calendar reminders
```sql
CREATE TABLE reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    message TEXT NOT NULL,
    first_run_at TEXT NOT NULL,
    remaining_repeats INTEGER NOT NULL,
    last_sent_at TEXT NULL,
    created_at TEXT NOT NULL
);
```

**inbox_log** - Email deduplication
```sql
CREATE TABLE inbox_log (
    uid TEXT PRIMARY KEY,
    from_email TEXT NOT NULL,
    received_at TEXT NOT NULL,
    subject TEXT,
    body_hash TEXT
);
```

### Scheduled Jobs

1. **Inbox Check** - Every 1 minute
   - Fetches unseen emails via IMAP
   - Parses commands and replies
   - Logs for deduplication

2. **Reminder Delivery** - Every 1 minute
   - Sends due calendar reminders
   - Handles repeat scheduling
   - Cleans up completed reminders

3. **Daily Weather** - 05:00 local time
   - Fetches forecasts for all subscribers
   - Generates clothing recommendations
   - Sends personalized weather reports

## 🔧 Configuration Details

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EMAIL_ADDRESS` | ✅ | - | Service email address |
| `EMAIL_PASSWORD` | ✅ | - | Email password/app password |
| `IMAP_HOST` | ✅ | - | IMAP server hostname |
| `SMTP_HOST` | ✅ | - | SMTP server hostname |
| `IMAP_PORT` | ❌ | 993 | IMAP port (usually 993 for SSL) |
| `SMTP_PORT` | ❌ | 587 | SMTP port (587 for TLS, 465 for SSL) |
| `SMTP_USE_TLS` | ❌ | true | Use TLS for SMTP |
| `TZ` | ❌ | Europe/Bratislava | Timezone for scheduling |

### Weather Data

Uses **Open-Meteo APIs** (free, no registration required):

- **Geocoding**: `https://geocoding-api.open-meteo.com/v1/search`
- **Weather**: `https://api.open-meteo.com/v1/forecast`

Weather reports include:
- Daily high/low temperatures
- Precipitation probability and amount
- Maximum wind speed
- Intelligent clothing recommendations

### Email Parsing

The service intelligently parses email bodies:

1. **Delete Command**: Exact text `delete` (case-insensitive)
2. **Calendar Format**: Contains `date=`, `time=`, or `message=`
3. **Location**: Everything else treated as weather location

## 🚨 Troubleshooting

### Common Issues

**"Required environment variable EMAIL_ADDRESS is not set"**
- Set all required environment variables before running

**"IMAP connection error"**
- Check IMAP_HOST, IMAP_PORT, and credentials
- Enable "Less secure app access" or use app passwords

**"No geocoding results for: XYZ"**
- Try more specific location names
- Use format: "City, Country" or "City, State, Country"

**"Couldn't parse date/time"**
- Use clear formats: "2025-12-01 08:30" or "tomorrow 2pm"
- Avoid ambiguous dates

### Debug Mode

Run with `--dry-run` to test without sending emails:

```bash
python app.py --dry-run
```

Check logs in `app.log` for detailed error information.

## 🔒 Security Notes

- 🔐 Uses SSL/TLS for all email connections
- 🗃️ Stores only necessary data in local SQLite database
- 🔑 No external API keys required
- 📧 Email passwords should use app-specific passwords
- 👤 Run with minimal system privileges
- 🚫 Sensitive files excluded via `.gitignore`

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and test thoroughly
4. **Commit your changes**: `git commit -m 'Add amazing feature'`
5. **Push to the branch**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Run with debug logging
python app.py --dry-run
```

### Code Style

- Follow PEP 8 Python style guidelines
- Add docstrings to all functions
- Include type hints where appropriate
- Write tests for new features

## 🐛 Issues & Support

- 🐞 **Bug Reports**: Contact filip.johanes9@gmail.com
- 💡 **Feature Requests**: Contact for commercial licensing inquiries
- ❓ **Questions**: Personal use support available via email

## 📝 License & Copyright

**© 2025 Filip Johanes. All Rights Reserved.**

This project is **PROPRIETARY SOFTWARE** under a restrictive license:

⚠️ **Commercial use PROHIBITED**  
⚠️ **Redistribution PROHIBITED**  
⚠️ **Selling or licensing PROHIBITED**  
✅ **Personal use only**  
✅ **Educational study allowed**

This software contains unique intellectual property including:
- Proprietary multi-language localization system
- Custom email processing algorithms
- Innovative weather delivery architecture

**Any commercial use or redistribution will result in legal action.**

For commercial licensing inquiries, contact: filip.johanes9@gmail.com

See the [LICENSE](LICENSE) file for complete terms and conditions.

## 🙏 Acknowledgments

- **Open-Meteo**: Free weather API service
- **Python Community**: For excellent libraries and tools

---

**Made with ❤️ for the open-source community**