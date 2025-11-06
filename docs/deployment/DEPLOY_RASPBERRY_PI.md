# 🥧 Raspberry Pi Deployment Guide

## Hardware Requirements
- Raspberry Pi 4B (2GB+ RAM recommended)
- MicroSD card (16GB+)
- Power supply
- Network connection (WiFi or Ethernet)

## Setup Process (30 minutes)

### 1. **Install Raspberry Pi OS**
```bash
# Flash Raspberry Pi OS Lite to SD card
# Enable SSH in raspi-config
# Connect to network
```

### 2. **Connect and Update**
```bash
# SSH into your Pi
ssh pi@raspberry-pi-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11+ (if not already installed)
sudo apt install python3 python3-pip python3-venv git -y
```

### 3. **Deploy the Application**
```bash
# Clone your repository
git clone https://github.com/FilipJohanes/reminderAPP.git
cd reminderAPP

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. **Configure Environment**
```bash
# Copy and edit config
cp .env.example .env
nano .env

# Add your email settings
EMAIL_ADDRESS=your-service-email@gmail.com
EMAIL_PASSWORD=your-app-password
IMAP_HOST=imap.gmail.com
SMTP_HOST=smtp.gmail.com
TZ=Europe/Bratislava
```

### 5. **Test the Service**
```bash
# Test configuration
python app.py --send-test your-email@gmail.com

# Run dry-run mode
python app.py --dry-run
```

### 6. **Create System Service**
```bash
# Create service file
sudo nano /etc/systemd/system/daily-brief.service
```

Service file content:
```ini
[Unit]
Description=Daily Brief Email Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/reminderAPP
Environment=PATH=/home/pi/reminderAPP/venv/bin
ExecStart=/home/pi/reminderAPP/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 7. **Enable and Start Service**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable daily-brief

# Start service now
sudo systemctl start daily-brief

# Check status
sudo systemctl status daily-brief

# View logs
sudo journalctl -u daily-brief -f
```

### 8. **Monitoring Commands**
```bash
# Check service status
sudo systemctl status daily-brief

# View recent logs
sudo journalctl -u daily-brief --since "1 hour ago"

# Restart service
sudo systemctl restart daily-brief

# Stop service
sudo systemctl stop daily-brief
```

## Advantages of Raspberry Pi
✅ **Low power consumption** (~3-5W vs 100-300W PC)
✅ **Always-on reliability** 
✅ **Dedicated service** (won't interfere with daily PC use)
✅ **Auto-restart** after power outages
✅ **Remote SSH management**
✅ **Cost effective** ($35-75 one-time cost)
✅ **Silent operation**

## Pi-Specific Optimizations
```bash
# Reduce GPU memory (more RAM for service)
sudo raspi-config
# Advanced Options > Memory Split > Set to 16

# Enable log rotation to prevent disk filling
sudo nano /etc/logrotate.d/daily-brief
```

Logrotate config:
```
/home/pi/reminderAPP/app.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```