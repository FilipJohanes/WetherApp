# Daily Brief Service - Setup & Operations Guide

Complete guide for deploying and operating Daily Brief on Raspberry Pi (backend) and Railway (frontend).

---

## Architecture Overview

```
┌─────────────────┐         HTTPS/API         ┌──────────────────┐
│   Railway       │ ─────────────────────────> │  Raspberry Pi    │
│   (Frontend)    │    REST API Calls          │  (Backend)       │
│                 │ <───────────────────────── │                  │
│  • web_app.py   │    JSON Responses          │  • app.py        │
│  • templates/   │                            │  • api.py        │
│  • static/      │                            │  • services/     │
└─────────────────┘                            │  • app.db        │
                                               └──────────────────┘
```

**Backend (Raspberry Pi)**:
- `app.py` - Email monitoring & scheduled jobs
- `api.py` - REST API server (port 5001)
- `services/` - Business logic modules
- `app.db` - SQLite database

**Frontend (Railway)**:
- `web_app.py` - Flask web interface
- `api_client.py` - Backend API client
- Templates & static files

---

## Part 1: Raspberry Pi Backend Setup

### Requirements

- Raspberry Pi (any model with network)
- Raspberry Pi OS Lite (64-bit)
- Internet connection
- Email account (Gmail/Outlook)

### Step 1: System Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y git python3 python3-pip python3-venv

# Clone repository
cd ~
git clone https://github.com/yourusername/reminderAPP.git
cd reminderAPP

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt
```

### Step 2: Email Configuration

Create Gmail app password (if using Gmail):
1. Go to Google Account → Security
2. Enable 2-Step Verification
3. Generate App Password (select "Mail" and your device)
4. Copy 16-character password

### Step 3: Configure Environment

```bash
# Generate API keys
python3 -c "import secrets; print('API_KEYS=' + secrets.token_urlsafe(32))"

# Copy and edit .env file
cp example.env .env
nano .env
```

Edit `.env`:
```bash
# Email Settings (REQUIRED)
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-16-char-app-password
IMAP_HOST=imap.gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true

# Timezone & Language
TZ=Europe/Bratislava
LANGUAGE=en

# API Settings (for frontend connection)
API_PORT=5001
API_KEYS=<paste-generated-key-from-above>

# Database
APP_DB_PATH=app.db
```

### Step 4: Initialize Database

```bash
# Create database
python3 -c "from app import init_db; init_db()"

# Verify database
ls -lh app.db
```

### Step 5: Test Backend Services

```bash
# Test API server
python3 api.py
# Should show: "🚀 Starting Daily Brief REST API"
# In another terminal: curl http://localhost:5001/health

# Test main app
python3 app.py
# Should show email monitoring starting
```

### Step 6: Setup Systemd Services

Create service file for app.py:
```bash
sudo nano /etc/systemd/system/dailybrief.service
```

Content:
```ini
[Unit]
Description=Daily Brief Email Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/reminderAPP
Environment="PATH=/home/pi/reminderAPP/venv/bin"
ExecStart=/home/pi/reminderAPP/venv/bin/python3 /home/pi/reminderAPP/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Create service file for api.py:
```bash
sudo nano /etc/systemd/system/dailybrief-api.service
```

Content:
```ini
[Unit]
Description=Daily Brief REST API
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/reminderAPP
Environment="PATH=/home/pi/reminderAPP/venv/bin"
ExecStart=/home/pi/reminderAPP/venv/bin/python3 /home/pi/reminderAPP/api.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services (start on boot)
sudo systemctl enable dailybrief
sudo systemctl enable dailybrief-api

# Start services now
sudo systemctl start dailybrief
sudo systemctl start dailybrief-api

# Check status
sudo systemctl status dailybrief
sudo systemctl status dailybrief-api
```

### Step 7: Setup Network Access

Choose ONE option:

**Option A: ngrok (Easiest, for testing)**
```bash
# Install ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm64.tgz
tar xvzf ngrok-*.tgz
sudo mv ngrok /usr/local/bin/

# Authenticate (get token from ngrok.com)
ngrok config add-authtoken YOUR_TOKEN

# Start tunnel
ngrok http 5001

# Copy the HTTPS URL (e.g., https://abc123.ngrok-free.app)
# Use this as BACKEND_API_URL in Railway
```

**Option B: Tailscale VPN (Recommended, secure)**
```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Start and authenticate
sudo tailscale up

# Get Tailscale IP
tailscale ip -4
# Use http://TAILSCALE_IP:5001 as BACKEND_API_URL
```

**Option C: Port Forwarding (Requires router access)**
1. Log into your router
2. Forward external port (e.g., 5001) → Pi IP:5001
3. Use http://YOUR_PUBLIC_IP:5001 as BACKEND_API_URL
4. ⚠️ Security risk - ensure strong API key!

---

## Part 2: Railway Frontend Deployment

### Step 1: Prepare Repository

Ensure these files are in your GitHub repo:
- `web_app.py`
- `api_client.py`
- `templates/`
- `static/`
- `Procfile`
- `requirements.txt`

### Step 2: Generate Frontend Keys

```bash
python3 -c "import secrets; print('FLASK_SECRET_KEY=' + secrets.token_hex(32))"
```

### Step 3: Deploy to Railway

1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your reminderAPP repository
4. Railway will detect Procfile and auto-deploy

### Step 4: Configure Environment Variables

In Railway Dashboard → Variables, add:

```
FLASK_SECRET_KEY=<generated-from-step-2>
BACKEND_API_URL=<your-pi-url-from-part1-step7>
BACKEND_API_KEY=<same-as-API_KEYS-on-pi>
```

Example:
```
FLASK_SECRET_KEY=a1b2c3d4e5f6...
BACKEND_API_URL=https://abc123.ngrok-free.app
BACKEND_API_KEY=your-generated-api-key
```

### Step 5: Deploy and Test

1. Railway auto-deploys on push
2. Get your Railway URL: `https://yourapp.up.railway.app`
3. Visit URL and test registration/login
4. Check Raspberry Pi logs for incoming API requests

---

## Part 3: Operations & Maintenance

### Monitoring Backend (Raspberry Pi)

```bash
# View service logs
sudo journalctl -u dailybrief -f
sudo journalctl -u dailybrief-api -f

# Check service status
sudo systemctl status dailybrief
sudo systemctl status dailybrief-api

# Restart services
sudo systemctl restart dailybrief
sudo systemctl restart dailybrief-api

# View application logs
tail -f ~/reminderAPP/app.log
tail -f ~/reminderAPP/web_app.log
```

### Monitoring Frontend (Railway)

- View logs in Railway Dashboard
- Check deployment status
- Monitor resource usage

### Database Backup

```bash
# Manual backup
cp ~/reminderAPP/app.db ~/reminderAPP/backups/app.db.$(date +%Y%m%d)

# Automated daily backup (crontab)
crontab -e
# Add: 0 2 * * * cp ~/reminderAPP/app.db ~/reminderAPP/backups/app.db.$(date +\%Y\%m\%d)
```

### Updating Code

**Backend (Raspberry Pi):**
```bash
cd ~/reminderAPP
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart dailybrief
sudo systemctl restart dailybrief-api
```

**Frontend (Railway):**
```bash
# Just push to GitHub - Railway auto-deploys
git push origin main
```

### Common Issues

**Backend API not accessible from Railway:**
- Check firewall: `sudo ufw status`
- Verify API is running: `curl http://localhost:5001/health`
- Test from external: `curl http://YOUR_PI_IP:5001/health`
- Check ngrok/VPN is active

**"Invalid or missing API key":**
- Verify `API_KEYS` on Pi matches `BACKEND_API_KEY` on Railway exactly
- No extra spaces or quotes

**Database locked errors:**
- Only one app.py instance should run
- Check: `ps aux | grep app.py`
- Stop duplicates: `sudo systemctl stop dailybrief`

**Email not sending:**
- Check email credentials in .env
- Verify IMAP/SMTP settings for your provider
- Check logs: `sudo journalctl -u dailybrief -f`

### Performance Tuning

**For Raspberry Pi Zero/Low RAM:**
```bash
# Add swap space
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set: CONF_SWAPSIZE=1024
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

**Reduce memory usage:**
- Use `python3 -O` for optimized mode
- Reduce Flask workers in Procfile if needed

---

## Part 4: Quick Reference

### Service Commands (Pi)

```bash
# Start
sudo systemctl start dailybrief
sudo systemctl start dailybrief-api

# Stop
sudo systemctl stop dailybrief
sudo systemctl stop dailybrief-api

# Restart
sudo systemctl restart dailybrief
sudo systemctl restart dailybrief-api

# Status
sudo systemctl status dailybrief
sudo systemctl status dailybrief-api

# Logs
sudo journalctl -u dailybrief -n 50
sudo journalctl -u dailybrief-api -n 50
```

### Health Checks

```bash
# Backend API
curl http://localhost:5001/health

# Check processes
ps aux | grep "python3 app.py"
ps aux | grep "python3 api.py"

# Database size
ls -lh ~/reminderAPP/app.db
```

### Test API Connection

```bash
cd ~/reminderAPP
python3 test_api_separation.py
```

---

## Part 5: Security Best Practices

1. **Strong API Keys**: Use 32+ character random keys
2. **Use HTTPS**: Deploy ngrok/VPN, not plain HTTP
3. **Regular Updates**: `sudo apt update && sudo apt upgrade`
4. **Firewall**: Only expose necessary ports
5. **Monitoring**: Set up log rotation and alerting
6. **Backups**: Automate daily database backups
7. **SSH Keys**: Disable password auth, use SSH keys only

---

## Support & Troubleshooting

### Logs Location

- Backend app: `~/reminderAPP/app.log`
- API server: `~/reminderAPP/api.log` (if configured)
- Systemd logs: `journalctl -u dailybrief`
- Railway logs: Dashboard → Logs tab

### Testing Flow

1. Test backend: `curl http://localhost:5001/health`
2. Test from Railway: Check Railway logs for API calls
3. Test registration: Create account on Railway frontend
4. Verify data: Check `app.db` on Pi for new user
5. Test weather: Subscribe and check preview

### Getting Help

1. Check logs first (both Pi and Railway)
2. Verify environment variables match
3. Test API connectivity: `test_api_separation.py`
4. Review this guide's troubleshooting section

---

## Appendix: File Structure

**Keep on Raspberry Pi:**
```
reminderAPP/
├── app.py              # Main service
├── api.py              # REST API
├── api_client.py       # (present but not used)
├── services/           # Business logic
├── app.db              # Database
├── .env                # Configuration
├── venv/               # Virtual environment
└── requirements.txt
```

**Deploy to Railway:**
```
reminderAPP/
├── web_app.py
├── api_client.py
├── templates/
├── static/
├── Procfile
└── requirements.txt
```

---

*Last Updated: December 2025*
