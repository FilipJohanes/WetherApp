# 🥧 Raspberry Pi Deployment Guide - Daily Brief Service

# ✅ NOTE: All instructions, commands, and examples in this guide have been reviewed and updated to match the current state of the WetherApp project (MVP2.0 branch, November 2025). If you spot any outdated information, please report it for immediate correction.

This guide walks you through deploying the **Daily Brief Service** (WetherApp MVP2.0) on your Raspberry Pi, making it a dedicated 24/7 weather and reminder email server. All instructions are up-to-date for the current codebase and deployment workflow.

## 📋 **Overview**

This guide will walk you through deploying the **Daily Brief Service** on your Raspberry Pi, making it a dedicated 24/7 weather email server.

---

## 🎯 **What You'll Need**

- **Raspberry Pi** (any model with network connectivity - Pi 3, 4, or Zero W recommended)
- **MicroSD card** (16GB+ recommended)
- **Power supply** for your Pi
- **Internet connection** (WiFi or Ethernet)
---

- **SSH access** or keyboard/monitor for initial setup
- **GitHub account credentials** (to clone the repository)

---

## 🚀 **Step-by-Step Deployment**

### **Step 1: Prepare Your Raspberry Pi**

#### 1.1 Install Raspberry Pi OS
```bash
# If you haven't already, flash Raspberry Pi OS Lite (64-bit) to your SD card
# Use Raspberry Pi Imager: https://www.raspberrypi.com/software/

# Enable SSH during imaging or after first boot:
sudo systemctl enable ssh
sudo systemctl start ssh
```

#### 1.2 Update System
```bash
# Update package lists
sudo apt update

# Upgrade existing packages
sudo apt upgrade -y

# Install essential tools
sudo apt install -y git python3 python3-pip python3-venv
```

#### 1.3 Set Timezone (Important for 5:00 AM scheduled emails!)
```bash
# Set to your timezone (example: Europe/Bratislava)
sudo timedatectl set-timezone Europe/Bratislava

# Verify timezone
timedatectl
```

---

### **Step 2: Clone and Setup the Application**

#### 2.1 Create Application Directory
```bash
# Create projects directory
cd ~/projects

# Clone the repository
git clone https://github.com/FilipJohanes/WetherApp.git
cd WetherApp
```

#### 2.2 Create Python Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Your prompt should now show (venv)
```

#### 2.3 Install Python Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list
```

---

### **Step 3: Configure Environment Variables**

#### 3.1 Create .env File
```bash
# Copy example configuration
cp .env.example .env

# Edit with your favorite editor (nano is easiest)
nano .env
```

#### 3.2 Configure Email Settings
Add these values to your `.env` file:

```env
# Email Configuration
EMAIL_ADDRESS=dailywether.reminder@gmail.com
EMAIL_PASSWORD=mxkz epiv xwxj zotq

# IMAP Settings (Gmail)
IMAP_HOST=imap.gmail.com
IMAP_PORT=993

# SMTP Settings (Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587

# Timezone (MUST match your location!)
TZ=Europe/Bratislava

# Optional: Logging
LOG_LEVEL=INFO
```

**Note:** The email password is an **App Password**, not your regular Gmail password.

Save and exit (Ctrl+X, then Y, then Enter in nano)

---

### **Step 4: Test the Application**

#### 4.1 Run Initial Test
```bash
# Make sure you're in the WetherApp directory with venv activated
cd ~/projects/WetherApp
source venv/bin/activate

# Run the test suite
python tests/test_runner.py
```

Select option `L` for localization tests or `A` for all safe tests.

#### 4.2 Test Main Application (Manual Run)
```bash
# Start the main application (it will run until you press Ctrl+C)
python app.py

# To run the web interface at the same time, open a second terminal or use tmux/screen:
python web_app.py

# You should see:
# - "Starting Daily Brief Service..."
# - Scheduler initialization
# - Email monitoring startup
# - Web app startup (if running web_app.py)

# Press Ctrl+C to stop gracefully in each terminal
```

---

### **Step 5: Setup Automatic Startup (systemd Service)**

#### 5.1 Create systemd Service File
```bash
# Create service file
sudo nano /etc/systemd/system/dailybrief.service
```

#### 5.2 Add Service Configuration
Paste this content (adjust paths if needed):

# Backend

```ini
[Unit]
Description=Daily Brief Weather Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/projects/WetherApp
Environment="PATH=/home/pi/projects/WetherApp/venv/bin"
ExecStart=/home/pi/projects/WetherApp/venv/bin/python /home/pi/projects/WetherApp/app.py
Restart=always
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

# Frontend 

```ini
[Unit]
Description=Daily Brief Web Interface
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/WetherApp
Environment="PATH=/home/pi/WetherApp/venv/bin"
ExecStart=/home/pi/WetherApp/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 web_app:app
Restart=always
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Note:** Using 4 workers on Raspberry Pi may cause high CPU usage. For Pi Zero/3, consider using 1-2 workers instead: `-w 2`

**Important:** Replace `/home/pi` with your actual home directory if different (use `echo $HOME` to check).

Save and exit (Ctrl+X, then Y, then Enter)

#### 5.3 Enable and Start Service
```bash
# Reload systemd to recognize new service
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable dailybrief.service

# Start the service now
sudo systemctl start dailybrief.service

# Check service status
sudo systemctl status dailybrief.service
```

You should see "active (running)" in green! ✅

#### 5.4 Disable and Enable webservice

```bash
#If running with systemd
sudo systemctl stop dailybrief.service

#If running Gunicorn manually:
pkill gunicorn

#Check that all related processes are stopped
sudo lsof -i :5000

#Start the web service again
#If using systemd:
sudo systemctl start dailybrief.service

#If running Gunicorn manually
gunicorn -w 4 -b 0.0.0.0:5000 web_app:app

#If running Flask manually
python web_app.py

#Check status and logs
sudo systemctl status dailybrief.service
sudo journalctl -u dailybrief.service -n 50

```
---

### **Step 6: Monitor and Manage**

#### 6.1 Useful Commands
```bash
# Check service status
sudo systemctl status dailybrief.service

# View real-time logs
sudo journalctl -u dailybrief.service -f

# View recent logs
sudo journalctl -u dailybrief.service -n 100

# Restart service
sudo systemctl restart dailybrief.service

# Stop service
sudo systemctl stop dailybrief.service

# Disable automatic startup
sudo systemctl disable dailybrief.service

# Shows active gunicorn tasks
sudo lsof -i :5000
```

#### 6.2 Application Logs
```bash
# View application log file
tail -f ~/projects/WetherApp/app.log

# View last 50 lines
tail -n 50 ~/projects/WetherApp/app.log
```

#### 6.3 Check Database
```bash
# View database contents
sqlite3 ~/projects/WetherApp/app.db

# Common SQL queries:
.tables                          # List all tables
SELECT * FROM subscribers;       # View all subscribers
SELECT * FROM inbox_log;         # View email processing log
.exit                            # Exit sqlite3
```
#### 6.3 DuckDNS setup/check
```bash

# Create a directory for DuckDNS
mkdir ~/duckdns
cd ~/duckdns

# nano duck.sh
nano duck.sh

# Make it executable
chmod 700 duck.sh

# Test it
./duck.sh
cat duck.log

# Set up the cron job
crontab -e

#Add this line
*/5 * * * * ~/duckdns/duck.sh >/dev/null 2>&1
``` 
---

### **Step 7: Update Application**

When you make changes to the code on your development machine:

```bash
# On Raspberry Pi:
cd ~/projects/WetherApp

# Activate virtual environment
source venv/bin/activate

# Pull latest changes
git fetch origin
git checkout "name"
git pull origin "name"

# Shows name of the pulled version
git log -1

# Install any new dependencies
pip install -r requirements.txt

# Restart the service
sudo systemctl restart dailybrief.service

# Check it's running properly
sudo systemctl status dailybrief.service
```

---

### **Step 8: Complete Reset and Fresh Setup**

If you need to completely reset your Raspberry Pi deployment and start fresh:

#### 8.1 Backup Current Data (IMPORTANT!)
```bash
# Create backup directory
mkdir -p ~/backups/dailybrief_reset_$(date +%Y%m%d)
cd ~/backups/dailybrief_reset_$(date +%Y%m%d)

# Backup database
cp ~/WetherApp/app.db ./app.db.backup

# Backup .env configuration
cp ~/WetherApp/.env ./.env.backup

# Backup any custom files
cp ~/WetherApp/*.log ./ 2>/dev/null || true

# Verify backups
ls -lh
echo "Backups saved in: $(pwd)"
```

#### 8.2 Stop All Running Services
```bash
# Stop dailybrief service (app.py)
sudo systemctl stop dailybrief.service
sudo systemctl disable dailybrief.service

# Stop web service if running as systemd
sudo systemctl stop dailybrief-web.service 2>/dev/null || true
sudo systemctl disable dailybrief-web.service 2>/dev/null || true

# Kill any remaining Python processes
pkill -f app.py
pkill -f web_app.py
pkill gunicorn

# Verify nothing is running on port 5000
sudo lsof -i :5000

# If anything is still running, force kill
# sudo kill -9 $(sudo lsof -t -i:5000)
```

#### 8.3 Remove Application and Services
```bash
# Remove systemd service files
sudo rm /etc/systemd/system/dailybrief.service
sudo rm /etc/systemd/system/dailybrief-web.service 2>/dev/null || true

# Reload systemd
sudo systemctl daemon-reload

# Remove application directory
cd ~
rm -rf ~/WetherApp

# Remove any cron jobs (if set)
crontab -e

        
        #*/5 * * * * ~/duckdns/duck.sh >/dev/null 2>&1
# Delete any lines related to WetherApp or dailybrief

# Clear systemd journal logs (optional)
sudo journalctl --vacuum-time=1s
```

#### 8.4 Fresh Installation
```bash
# Clone repository
git clone https://github.com/FilipJohanes/WetherApp.git
cd WetherApp

# Checkout the branch you want (MVP, main, etc.)
git checkout MVP

# Create fresh virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

#### 8.5 Restore or Reconfigure Settings
```bash
# Option A: Restore from backup
cp ~/backups/dailybrief_reset_*/app.db.backup ~/WetherApp/app.db
cp ~/backups/dailybrief_reset_*/.env.backup ~/WetherApp/.env

# Option B: Create fresh .env file
cp ~/WetherApp/example.env ~/WetherApp/.env
nano ~/WetherApp/.env
# Add your email credentials and settings

# Set proper permissions
chmod 600 ~/WetherApp/.env

# Option C: Initialize fresh database (if not restoring)
cd ~/WetherApp
source venv/bin/activate
python scripts/init_db.py
```

#### 8.6 Recreate systemd Services

**Create Backend Service (app.py):**
```bash
sudo nano /etc/systemd/system/dailybrief.service
```

Paste this configuration:
```ini
[Unit]
Description=Daily Brief Weather Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/projects/WetherApp
Environment="PATH=/home/pi/projects/WetherApp/venv/bin"
ExecStart=/home/pi/projects/WetherApp/venv/bin/python /home/pi/projects/WetherApp/app.py
Restart=always
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Create Web Service (web_app.py):**
```bash
sudo nano /etc/systemd/system/dailybrief-web.service
```

Paste this configuration:
```ini
[Unit]
Description=Daily Brief Web Interface
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/WetherApp
Environment="PATH=/home/pi/WetherApp/venv/bin"
ExecStart=/home/pi/WetherApp/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 web_app:app
Restart=always
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Note:** This uses 4 Gunicorn workers. For Raspberry Pi Zero or Pi 3 with limited RAM, consider reducing to 1-2 workers: `-w 2`

**Important:** Replace `/home/pi` with your actual home directory if different.

#### 8.7 Start Fresh Services
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services to start on boot
sudo systemctl enable dailybrief.service
sudo systemctl enable dailybrief-web.service

# Start services
sudo systemctl start dailybrief.service
sudo systemctl start dailybrief-web.service

# Check status of both services
sudo systemctl status dailybrief.service
sudo systemctl status dailybrief-web.service

# View logs
sudo journalctl -u dailybrief.service -n 50
sudo journalctl -u dailybrief-web.service -n 50
```

#### 8.8 Verification
```bash
# Check both services are running
sudo systemctl status dailybrief.service
sudo systemctl status dailybrief-web.service

# Test web interface
curl http://localhost:5000

# Check database
cd ~/WetherApp
sqlite3 app.db "SELECT * FROM subscribers;"

# Monitor logs in real-time
sudo journalctl -u dailybrief.service -u dailybrief-web.service -f

# Verify timezone
timedatectl

# Check disk space
df -h

# Check memory
free -h
```

#### 8.9 Post-Reset Checklist

- [ ] Both services are active and running
- [ ] Database restored or reinitialized
- [ ] .env file configured with correct credentials
- [ ] Timezone set correctly
- [ ] Logs show no errors
- [ ] Web interface accessible (http://raspberry-pi-ip:5000)
- [ ] Email monitoring working (check logs)
- [ ] Services start automatically after reboot test

#### 8.10 Test Reboot
```bash
# Reboot to test auto-start
sudo reboot

# After Pi restarts, SSH back in and check:
sudo systemctl status dailybrief.service
sudo systemctl status dailybrief-web.service
```

---

##  **Troubleshooting**

### **Service Won't Start**
```bash
# Check detailed error logs
sudo journalctl -u dailybrief.service -n 50 --no-pager

# Check if Python path is correct
which python
# Should show: /home/pi/projects/WetherApp/venv/bin/python

# Test manually
cd ~/projects/WetherApp
source venv/bin/activate
python app.py
```

### **Email Not Sending**
```bash
# Check email credentials in .env
cat ~/projects/WetherApp/.env

# Test email connectivity
python -c "import smtplib; print('SMTP import OK')"

# Check logs for email errors
grep -i "email\|smtp\|error" ~/projects/WetherApp/app.log
```

### **Timezone Issues (Emails at Wrong Time)**
```bash
# Verify system timezone
timedatectl

# Should match your .env TZ setting
cat ~/projects/WetherApp/.env | grep TZ

# If different, update:
sudo timedatectl set-timezone Europe/Bratislava
sudo systemctl restart dailybrief.service
```

### **No Space Left on Device (During pip install)**
```bash
# Error: "could not write to... No space left on device"
# This happens when installing packages like timezonefinder on Pi

# COMMON CAUSE: /tmp is tmpfs (RAM-based) with limited space (usually 209M)
# Large packages like timezonefinder (53MB) exceed this during build

# SOLUTION 1: Use disk-based temporary directory (RECOMMENDED)
mkdir -p ~/pip_tmp
TMPDIR=~/pip_tmp pip install --no-cache-dir -r requirements.txt
rm -rf ~/pip_tmp

# SOLUTION 2: Install problem package separately with custom TMPDIR
mkdir -p ~/pip_tmp
TMPDIR=~/pip_tmp pip install --no-cache-dir timezonefinder
rm -rf ~/pip_tmp
# Then install remaining packages normally
pip install --no-cache-dir -r requirements.txt

# SOLUTION 3: Increase tmpfs size (if RAM allows)
# Check current /tmp size
df -h /tmp
# Edit fstab to increase tmpfs size
sudo nano /etc/fstab
# Add or modify this line:
# tmpfs /tmp tmpfs defaults,noatime,nosuid,size=512M 0 0
# Reboot to apply
sudo reboot

# If disk space is actually low:
# 1. Check disk space
df -h

# 2. Clean up unnecessary files
sudo journalctl --vacuum-time=7d
sudo apt clean
sudo apt autoremove -y
pip cache purge
rm -rf ~/.cache/pip

# 3. Check for large files
du -sh ~/* | sort -h | tail -10

# 4. Expand filesystem (if SD card is larger than current partition)
sudo raspi-config
# Select: Advanced Options -> Expand Filesystem
# Reboot after this
```

### **Web Interface Not Accessible (Port 5000)**
```bash
# Error: "Failed to connect to localhost port 5000"
# This means web_app.py is not running

# 1. Check if web service is running
sudo systemctl status dailybrief-web.service
# or
ps aux | grep web_app.py

# 2. Check logs for errors (MOST IMPORTANT!)
sudo journalctl -u dailybrief-web.service -n 100

# 3. Common Error: "ModuleNotFoundError: No module named 'bcrypt'"
# Solution: Install missing dependencies
sudo systemctl stop dailybrief-web.service
cd ~/WetherApp
source venv/bin/activate
mkdir -p ~/pip_tmp
TMPDIR=~/pip_tmp pip install --no-cache-dir -r requirements.txt
rm -rf ~/pip_tmp
sudo systemctl start dailybrief-web.service

# 4. Check if anything is using port 5000
sudo lsof -i :5000
sudo netstat -tlnp | grep 5000

# 5. If service doesn't exist, create it first (see Step 8.6 in this guide)
# Or start manually for testing:
cd ~/WetherApp
source venv/bin/activate
python web_app.py

# Web app should start on http://0.0.0.0:5000
# Test from Pi: curl http://localhost:5000
# Test from another device: http://raspberry-pi-ip:5000

# 6. If service exists but not running, start it:
sudo systemctl start dailybrief-web.service
sudo systemctl status dailybrief-web.service

# 7. Other common issues:
# - Port already in use (kill the other process)
# - Missing dependencies (see #3 above)
# - Database locked (stop other services accessing it)
# - Firewall blocking (sudo ufw allow 5000)

# 8. Enable service to start on boot
sudo systemctl enable dailybrief-web.service
```

### **Database Locked**
```bash
# If you get "database is locked" error:
# Stop the service
sudo systemctl stop dailybrief.service

# Check for zombie processes
ps aux | grep python

# Kill any zombie processes
kill -9 <process_id>

# Restart service
sudo systemctl start dailybrief.service
```

### **Out of Memory**
```bash
# Check memory usage
free -h

# If low, increase swap space (for Pi with limited RAM):
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Change CONF_SWAPSIZE=100 to CONF_SWAPSIZE=512
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### **CPU Spikes / High Load**
```bash
# Check what's using CPU
top -b -n 1 | head -n 20

# If Gunicorn workers are at 80-100% CPU:
# PROBLEM: Too many Gunicorn workers for Raspberry Pi's limited RAM
# SOLUTION: Kill gunicorn and use Flask dev server or single worker

# Kill all gunicorn processes
pkill gunicorn

# Option 1: Use Flask development server (RECOMMENDED for Pi)
cd ~/WetherApp
source venv/bin/activate
python web_app.py &

# Option 2: Use ONLY 1 Gunicorn worker (not 4!)
gunicorn -w 1 -b 0.0.0.0:5000 web_app:app &

# Verify CPU is back to normal
top -b -n 1 | head -n 20

# Common causes of CPU spikes:
# - Too many Gunicorn workers (use -w 1 max on Pi)
# - Database locking (check for zombie processes)
# - Memory pressure causing swap thrashing (check free -h)
```

---

## 🔒 **Security Best Practices**

### **Secure Your .env File**
```bash
# Restrict file permissions (owner read/write only)
chmod 600 ~/WetherApp/.env

# Verify permissions
ls -la ~/WetherApp/.env
# Should show: -rw-------
```

### **Keep System Updated**
```bash
# Set up automatic security updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

### **Firewall Configuration (Optional)**
```bash
# Install UFW (Uncomplicated Firewall)
sudo apt install ufw

# Allow SSH
sudo ufw allow ssh

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

---

## 📊 **Performance Optimization**

### **Reduce Unnecessary Services**
```bash
# Disable Bluetooth (if not needed)
sudo systemctl disable bluetooth

# Disable WiFi (if using Ethernet)
sudo systemctl disable wpa_supplicant
```

### **Monitor Resource Usage**
```bash
# Install htop for better monitoring
sudo apt install htop

# Run htop
htop

# Check CPU temperature
vcgencmd measure_temp
```

---

## 🎯 **Scheduled Email Times**

The service sends daily weather emails at:
- **5:00 AM** (local timezone set in .env)

To change this, edit `app.py` and find the scheduler configuration:
```python
scheduler.add_job(send_daily_briefs, 'cron', hour=5, minute=0)
```

Change `hour=5` to your preferred hour (24-hour format).

After editing:
```bash
sudo systemctl restart dailybrief.service
```

---

## 📧 **Managing Subscribers**

### **Add Subscriber via Email**
Send an email to `dailywether.reminder@gmail.com` with:
```
subscribe
location: Bratislava, Slovakia
language: sk
personality: emuska
```

### **Add Subscriber Manually (Database)**
```bash
cd ~/projects/WetherApp
sqlite3 app.db

-- Update for current schema (example, adjust as needed):
INSERT INTO subscribers (email, location, personality, language, active, created_at)
VALUES ('em.solarova@gmail.com', 'Bratislava', 'emuska', 'sk', 1, CURRENT_TIMESTAMP);

.exit
```

### **View All Subscribers**
```bash
cd ~/projects/WetherApp
sqlite3 app.db "SELECT email, location, personality, language, active FROM subscribers;"
```

---

## 🔄 **Backup Strategy**

### **Backup Database**
```bash
# Create backup script
nano ~/backup_dailybrief.sh
```

Add this content:
```bash
#!/bin/bash
BACKUP_DIR=~/backups/dailybrief
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d_%H%M%S)
cp ~/projects/WetherApp/app.db $BACKUP_DIR/app_db_$DATE.db
echo "Backup created: $BACKUP_DIR/app_db_$DATE.db"

# Keep only last 30 backups
cd $BACKUP_DIR
ls -t | tail -n +31 | xargs rm -f 2>/dev/null
```

Make executable and run:
```bash
chmod +x ~/backup_dailybrief.sh
./backup_dailybrief.sh
```

### **Schedule Automatic Backups**
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /home/pi/backup_dailybrief.sh
```

---

## 🌐 **Remote Access (Optional)**

### **Setup VNC for GUI Access**
```bash
# Enable VNC
sudo raspi-config
# Select: Interface Options -> VNC -> Enable

# Install VNC viewer on your computer:
# https://www.realvnc.com/en/connect/download/viewer/
```

### **Setup SSH Key Authentication**
On your computer:
```bash
# Generate SSH key (if you don't have one)
ssh-keygen -t ed25519

# Copy to Raspberry Pi
ssh-copy-id pi@<raspberry-pi-ip>

# Now you can SSH without password
ssh pi@<raspberry-pi-ip>
```

### **Updating pi**

```bash
# Fetch all remote changes without merging them
git fetch --all

# Switch to the branch you want to be on
git checkout your-branch-name

# Pull the latest changes from the remote branch into your local branch
git pull

# Forcefully reset your local branch to match the remote branch exactly
git reset --hard origin/your-branch-name

# Check the current status of your working directory
git status

# (Optional) Remove any untracked files or directories if you want a completely clean slate
git clean -f -d

```
---

## 🎉 **Verification Checklist**

After deployment, verify everything is working:

- [ ] System timezone is correct (`timedatectl`)
- [ ] Service is active and running (`sudo systemctl status dailybrief.service`)
- [ ] Logs show no errors (`sudo journalctl -u dailybrief.service -n 50`)
- [ ] Database contains subscribers (`sqlite3 app.db "SELECT * FROM subscribers;"`)
- [ ] Email credentials are correct (test by running `python app.py` manually)
- [ ] Service starts automatically after reboot (`sudo reboot`, then check status)
- [ ] Weather API is accessible (check logs for weather fetch attempts)
- [ ] Disk space is adequate (`df -h`)
- [ ] Memory usage is reasonable (`free -h`)

---

## 📞 **Support**

If you encounter issues:

1. Check logs: `sudo journalctl -u dailybrief.service -n 100`
2. Test manually: `cd ~/projects/WetherApp && source venv/bin/activate && python app.py`
3. Review this guide's Troubleshooting section
4. Check GitHub issues: https://github.com/FilipJohanes/WetherApp/issues

**Developer:** Filip Johanes  
**Email:** filip.johanes9@gmail.com  
**Repository:** https://github.com/FilipJohanes/WetherApp

---

## 🌟 **Next Steps**

Once deployed:
- Monitor the first few days to ensure emails are sent at 5:00 AM
- Check that subscribers receive their personalized weather emails
- Enjoy your **Slovak emuska personality** messages! 💖
- The service will run 24/7 automatically

**Congratulations!** 🎉 Your Daily Brief Service is now running on Raspberry Pi!

---

*Last Updated: November 7, 2025*
