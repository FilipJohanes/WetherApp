# 🚀 Daily Brief Service - Production Deployment Guide

## 📋 Quick Setup (5 minutes)

### 1. **Environment Setup**
```bash
# Clone or download the project
cd reminderAPP

# Install dependencies
pip install -r requirements.txt
```

### 2. **Email Configuration** 
Create `.env` file with your Gmail credentials:
```bash
EMAIL_ADDRESS=your-service-email@gmail.com
EMAIL_PASSWORD=your-app-password
IMAP_HOST=imap.gmail.com
SMTP_HOST=smtp.gmail.com
TZ=Europe/Bratislava
```

> 💡 **Important**: Use Gmail App Password, not your regular password!
> Go to: Google Account → Security → 2-Step Verification → App Passwords

### 3. **Test the Service**
```bash
# Test run (won't send emails)
python app.py --dry-run

# Production run
python app.py
```

## 📧 **How Users Interact**

### **Weather Subscription**
Users send emails to your service email:
```
Subject: Weather Request
Body: Prague, Czech Republic
```

Service responds with confirmation and starts daily 5 AM forecasts.

### **Personality & Language**
```
Subject: Settings
Body: cute           # Changes to cute personality
Body: es            # Changes to Spanish language
Body: brutal        # Changes to brutal personality
```

### **Unsubscribe**
```
Subject: Stop
Body: delete
```

## 🌟 **Current Features**

✅ **Weather Service**: Daily forecasts at 05:00 local time  
✅ **4 Personalities**: neutral, cute, brutal, emuska  
✅ **3 Languages**: English, Spanish, Slovak  
✅ **Smart Parsing**: Handles multi-line emails and system emails  
✅ **Unicode Support**: Works with international characters  
✅ **Production Ready**: Crash recovery, duplicate handling  

❌ **Reminder System**: Temporarily disabled (will re-enable later)

## 🔧 **Production Deployment**

### **Windows Service**
```powershell
# Run as background service
python app.py --service
```

### **Linux systemd**
Create `/etc/systemd/system/daily-brief.service`:
```ini
[Unit]
Description=Daily Brief Weather Service
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/reminderAPP
ExecStart=/usr/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable: `sudo systemctl enable daily-brief.service`

### **Docker** (Optional)
```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
```

## 📊 **Monitoring**

Service logs to console with timestamps:
```
2025-11-06 05:00:01 - INFO - Sending weather to 5 subscribers
2025-11-06 05:00:15 - INFO - Weather sent to user@example.com
```

## 🔮 **Future Roadmap**

1. **Mobile App** - React Native/Flutter app
2. **Reminder System** - Re-enable calendar reminders 
3. **Web Dashboard** - User management interface
4. **Telegram Bot** - Alternative to email
5. **Advanced Features** - Weather alerts, custom schedules

---

**Need help?** The service is stable and production-ready for weather functionality! 🌟