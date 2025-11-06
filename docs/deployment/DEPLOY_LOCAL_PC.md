# 🖥️ Local PC Deployment Guide

## Quick Setup (5 minutes)

### 1. **Prepare Your Environment**
```bash
# Navigate to your project
cd c:\Projects\reminderAPP

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. **Configure Email Settings**
```bash
# Copy example config
copy .env.example .env

# Edit .env with your email settings
notepad .env
```

Required settings:
```env
EMAIL_ADDRESS=your-service-email@gmail.com
EMAIL_PASSWORD=your-16-char-app-password
IMAP_HOST=imap.gmail.com
SMTP_HOST=smtp.gmail.com
```

### 3. **Test Configuration**
```bash
# Test email setup
python app.py --send-test your-personal-email@gmail.com

# Run in dry-run mode first
python app.py --dry-run
```

### 4. **Start the Service**
```bash
# Run normally (will show logs in console)
python app.py

# Or run as Windows background task
# Create a batch file: start_service.bat
@echo off
cd /d "c:\Projects\reminderAPP"
venv\Scripts\activate
python app.py
```

### 5. **Keep It Running (Windows)**
- **Option A:** Leave PowerShell window open
- **Option B:** Use Windows Task Scheduler
- **Option C:** Use NSSM (Non-Sucking Service Manager)

## Windows Task Scheduler Setup

1. Open Task Scheduler
2. Create Basic Task
3. Name: "Daily Brief Service"
4. Trigger: At startup
5. Action: Start program
6. Program: `C:\Projects\reminderAPP\venv\Scripts\python.exe`
7. Arguments: `app.py`
8. Start in: `C:\Projects\reminderAPP`
9. Check "Run with highest privileges"

## Pros/Cons
✅ **Pros:**
- Zero cost
- Full control
- Easy debugging
- Instant deployment

❌ **Cons:**
- PC must stay on 24/7
- No automatic restart if PC reboots
- Power consumption