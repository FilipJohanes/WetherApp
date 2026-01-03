# 📬 Daily Brief Service

![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)
![License](https://img.shields.io/badge/license-Proprietary-red.svg)
![Platform](https://img.shields.io/badge/platform-linux%20%7C%20raspberry%20pi-lightgrey.svg)

> 🚀 **Multi-language email-driven weather & reminder service**  
> **© 2025 Filip Johanes. All Rights Reserved.**

Automated daily weather forecasts and reminders delivered via email. Backend runs on Raspberry Pi, web interface hosted on Railway.

## ⚠️ SECURITY WARNING

**This application MUST be deployed with HTTPS/SSL in production!**

Passwords and sensitive data are transmitted over the network and MUST be encrypted with TLS/SSL. See [SECURITY.md](SECURITY.md) for setup instructions.

**Never deploy this application over plain HTTP on a public network.**

---

## Features

- **🌤️ Daily Weather** - Location-based forecasts at 05:00 local time
- **📧 Email Control** - Subscribe/unsubscribe via simple email commands
- **🌍 Multi-Language** - English, Spanish, Slovak
- **🎭 Personality Modes** - Neutral, cute, brutal communication styles
- **⏰ Smart Scheduling** - Timezone-aware delivery
- **🔒 Secure** - API authentication, rate limiting, CSRF protection
- **📱 Web Interface** - User registration, subscription management
- **🔄 Separated Architecture** - Backend on Pi, frontend on cloud

---

## Architecture

```
┌──────────────┐         REST API          ┌─────────────────┐
│   Railway    │ ─────────────────────────> │  Raspberry Pi   │
│  (Frontend)  │   Authentication/Data      │   (Backend)     │
│ web_app.py   │ <───────────────────────── │ app.py + api.py │
└──────────────┘                            └─────────────────┘
                                                     │
                                                     ▼
                                             ┌──────────────┐
                                             │  SQLite DB   │
                                             └──────────────┘
```

**Backend (Raspberry Pi)**:
- Email monitoring & scheduled jobs
- REST API for web frontend
- Database management

**Frontend (Railway/Cloud)**:
- Web registration & login
- Subscription management UI
- Communicates with backend via API

---

## Quick Start

### Prerequisites

- Raspberry Pi with Raspberry Pi OS
- Email account (Gmail/Outlook)
- Railway account (for frontend deployment)

### 1. Backend Setup (Raspberry Pi)

```bash
# Clone repository
git clone https://github.com/yourusername/reminderAPP.git
cd reminderAPP

# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp example.env .env
nano .env  # Add email credentials and API key

# Initialize database
python3 -c "from app import init_db; init_db()"

# Start services
python3 api.py &   # REST API
python3 app.py     # Email service
```

### 2. Frontend Setup (Railway)

1. Push repository to GitHub
2. Deploy to Railway
3. Set environment variables:
   - `FLASK_SECRET_KEY`
   - `BACKEND_API_URL` (your Pi's API endpoint)
   - `BACKEND_API_KEY` (matches Pi's API_KEYS)

---

## Project Structure

```
reminderAPP/
├── app.py                  # Main email monitoring service
├── api.py                  # REST API server
├── web_app.py              # Web frontend
├── api_client.py           # API client library
│
├── services/               # Business logic
│   ├── email_service.py
│   ├── weather_service.py
│   ├── user_service.py
│   ├── countdown_service.py
│   └── reminder_service.py
│
├── templates/              # Web UI templates
├── static/                 # CSS, JS, images
├── languages/              # Multi-language support
│   ├── en/
│   ├── es/
│   └── sk/
│
├── scripts/                # Utility scripts
├── tests/                  # Test suite
└── docs/                   # Documentation
    ├── SETUP_AND_OPERATIONS.md  # Complete setup guide
    └── CONTRIBUTING.md          # Development guidelines
```

---

## Usage

### Email Commands

Send email to your configured address:

- **Subscribe**: `Berlin, Germany` (just send location)
- **Unsubscribe**: `unsubscribe` or `STOP`
- **Change Location**: `Paris, France` (sends new location)
- **Change Language**: `language: es` (switch to Spanish)
- **Change Personality**: `personality: cute` (neutral/cute/brutal)

### Web Interface

Visit your Railway URL:
- Register account
- Manage weather subscriptions
- Add countdowns & reminders
- Preview daily emails
- View statistics

---

## Documentation

- **[Setup & Operations Guide](docs/SETUP_AND_OPERATIONS.md)** - Complete deployment guide
- **[Contributing Guide](docs/CONTRIBUTING.md)** - Development guidelines
- **[License](LICENSE)** - Proprietary license

---

## Configuration

### Backend (.env on Raspberry Pi)

```bash
# Email Settings
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
IMAP_HOST=imap.gmail.com
SMTP_HOST=smtp.gmail.com

# API Settings
API_PORT=5001
API_KEYS=your-secure-api-key

# Optional
TZ=Europe/Bratislava
LANGUAGE=en
```

### Frontend (Railway Variables)

```bash
FLASK_SECRET_KEY=your-secret-key
BACKEND_API_URL=http://your-pi-ip:5001
BACKEND_API_KEY=same-as-backend
```

---

## Monitoring

### Backend (Raspberry Pi)

```bash
# View logs
sudo journalctl -u dailybrief -f
sudo journalctl -u dailybrief-api -f

# Service status
sudo systemctl status dailybrief
sudo systemctl status dailybrief-api
```

### Frontend (Railway)

- View logs in Railway Dashboard
- Monitor deployments
- Check environment variables

---

## Security

- ✅ API key authentication
- ✅ Rate limiting (Flask-Limiter)
- ✅ CSRF protection
- ✅ Input validation & sanitization
- ✅ Password hashing (bcrypt)
- ✅ SQL injection prevention
- ✅ XSS protection

---

## Requirements

- Python 3.11+
- SQLite 3
- Internet connection
- Email account
- Raspberry Pi (any model)

---

## Support

For issues, questions, or contributions:
1. Check [docs/SETUP_AND_OPERATIONS.md](docs/SETUP_AND_OPERATIONS.md)
2. Review systemd logs on Raspberry Pi
3. Check Railway deployment logs
4. Verify environment variables

---

## License

**Proprietary Software** - All Rights Reserved  
© 2025 Filip Johanes

This software contains proprietary algorithms and features. Commercial use, redistribution, or derivative works are strictly prohibited without explicit written permission.

See [LICENSE](LICENSE) for full terms.

---

*Last Updated: December 2025*
