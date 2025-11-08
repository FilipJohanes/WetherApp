# 🔒 Secure Flask Web Interface - Deployment Guide

## 🛡️ Security Features Implemented

✅ **CSRF Protection** - Prevents cross-site request forgery attacks  
✅ **Rate Limiting** - Blocks spam and DDoS attempts  
✅ **Input Validation** - Strict validation on all form inputs  
✅ **SQL Injection Prevention** - Parameterized queries only  
✅ **XSS Protection** - HTML escaping and secure headers  
✅ **Email Validation** - RFC-compliant email checking  
✅ **Secure Headers** - X-Frame-Options, CSP, etc.  
✅ **Secret Key Management** - Environment-based secrets  
✅ **Request Size Limits** - Max 16KB per request  

---

## 🚀 Deployment on Raspberry Pi

### **Step 1: Update Requirements**

```bash
cd ~/projects/WetherApp
source venv/bin/activate
pip install -r requirements.txt
```

This will install:
- Flask>=3.0.0
- Flask-WTF>=1.2.0 (CSRF protection)
- Flask-Limiter>=3.5.0 (rate limiting)
- email-validator>=2.1.0 (email validation)

---

### **Step 2: Generate Secret Key**

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output (64 character hex string).

---

### **Step 3: Add to .env File**

```bash
nano ~/projects/WetherApp/.env
```

Add this line (replace with your generated key):
```
FLASK_SECRET_KEY=your_64_character_hex_string_here
```

Save with `Ctrl+X`, `Y`, `Enter`.

**⚠️ IMPORTANT:** Keep this secret key private! Never commit to Git!

---

### **Step 4: Test Web App Locally**

```bash
cd ~/projects/WetherApp
source venv/bin/activate
python web_app.py
```

You should see:
```
Starting Daily Brief Web Interface
🔒 Security features enabled: CSRF, Rate Limiting, Input Validation
* Running on http://0.0.0.0:5000
```

Test by visiting: `http://192.168.1.198:5000`

Press `Ctrl+C` to stop.

---

### **Step 5: Create Systemd Service**

```bash
sudo nano /etc/systemd/system/dailybrief-web.service
```

Paste this content (update FLASK_SECRET_KEY):

```ini
[Unit]
Description=Daily Brief Web Interface
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/projects/WetherApp
Environment="PATH=/home/pi/projects/WetherApp/venv/bin"
Environment="FLASK_SECRET_KEY=your_secret_key_here"
ExecStart=/home/pi/projects/WetherApp/venv/bin/python /home/pi/projects/WetherApp/web_app.py
Restart=always
RestartSec=10

StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Save with `Ctrl+X`, `Y`, `Enter`.

---

### **Step 6: Enable and Start Service**

```bash
sudo systemctl daemon-reload
sudo systemctl enable dailybrief-web.service
sudo systemctl start dailybrief-web.service
```

---

### **Step 7: Verify Both Services Running**

```bash
sudo systemctl status dailybrief.service
sudo systemctl status dailybrief-web.service
```

Both should show **"active (running)"** in green! ✅

---

## 🔒 Security Checklist

### **Before Going Live:**

- [ ] Set unique FLASK_SECRET_KEY in `.env`
- [ ] Verify rate limiting is active (test by rapid requests)
- [ ] Test CSRF protection (form submissions without token fail)
- [ ] Check input validation (try SQL injection: `'; DROP TABLE--`)
- [ ] Verify XSS protection (try `<script>alert('xss')</script>`)
- [ ] Confirm secure headers (`curl -I http://192.168.1.198:5000`)
- [ ] Review logs for suspicious activity

---

## 🌐 Access Methods

### **Local Network:**
```
http://192.168.1.198:5000
```

### **From Internet (Optional - Advanced):**

#### **Option A: Port Forwarding (Simple)**
1. Log into your router admin panel
2. Forward port 5000 → 192.168.1.198:5000
3. Use your public IP or Dynamic DNS

**⚠️ Warning:** This exposes your Pi to the internet!

#### **Option B: Reverse Proxy with NGINX (Recommended)**

Install NGINX:
```bash
sudo apt install nginx
```

Create config:
```bash
sudo nano /etc/nginx/sites-available/dailybrief
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/dailybrief /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### **Option C: CloudFlare Tunnel (Most Secure)**

Use Cloudflare Tunnel for zero-port-forwarding:
```bash
# Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb
sudo dpkg -i cloudflared-linux-arm64.deb

# Authenticate
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create dailybrief

# Configure
cloudflared tunnel route dns dailybrief your-domain.com

# Run
cloudflared tunnel run dailybrief
```

---

## 🔐 Additional Security (Optional)

### **1. Enable HTTPS with Let's Encrypt:**

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### **2. Firewall (UFW):**

```bash
sudo apt install ufw
sudo ufw allow ssh
sudo ufw allow 5000/tcp
sudo ufw enable
```

### **3. Fail2Ban (Block Brute Force):**

```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## 📊 Monitoring

### **View Web Logs:**
```bash
sudo journalctl -u dailybrief-web.service -f
```

### **View Application Logs:**
```bash
tail -f ~/projects/WetherApp/web_app.log
```

### **Check Memory Usage:**
```bash
free -h
htop
```

---

## 🚨 Security Incidents

### **If You Suspect Attack:**

1. **Check logs immediately:**
   ```bash
   sudo journalctl -u dailybrief-web.service -n 500
   grep "error\|attack\|suspicious" ~/projects/WetherApp/web_app.log
   ```

2. **Stop service temporarily:**
   ```bash
   sudo systemctl stop dailybrief-web.service
   ```

3. **Review database:**
   ```bash
   sqlite3 ~/projects/WetherApp/app.db
   SELECT * FROM subscribers ORDER BY updated_at DESC LIMIT 10;
   .exit
   ```

4. **Change secret key:**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   nano ~/projects/WetherApp/.env  # Update FLASK_SECRET_KEY
   sudo systemctl restart dailybrief-web.service
   ```

---

## 🎯 Performance Tuning

### **For Production (Optional):**

Use Gunicorn instead of Flask dev server:

```bash
pip install gunicorn
```

Update service file:
```ini
ExecStart=/home/pi/projects/WetherApp/venv/bin/gunicorn -w 2 -b 0.0.0.0:5000 web_app:app
```

Benefits:
- ✅ Better performance
- ✅ Multiple workers
- ✅ Production-ready

---

## 📝 Security Best Practices

1. **Keep secrets secret** - Never commit `.env` to Git
2. **Update regularly** - `sudo apt update && sudo apt upgrade`
3. **Monitor logs** - Check for suspicious activity weekly
4. **Backup database** - Regular backups of `app.db`
5. **Rate limiting** - Adjust limits based on traffic
6. **Use HTTPS** - Always in production
7. **Firewall rules** - Only open necessary ports
8. **Strong passwords** - If adding admin panel later

---

## 🆘 Troubleshooting

### **Web service won't start:**
```bash
sudo journalctl -u dailybrief-web.service -n 50
```

### **403 Forbidden errors:**
Check file permissions:
```bash
ls -la ~/projects/WetherApp/
chmod 755 ~/projects/WetherApp/web_app.py
```

### **Database locked:**
```bash
sudo systemctl stop dailybrief.service dailybrief-web.service
# Wait 5 seconds
sudo systemctl start dailybrief.service dailybrief-web.service
```

### **Out of memory:**
Check current usage:
```bash
free -h
ps aux --sort=-%mem | head
```

---

## ✅ Verification Steps

After deployment, test these:

1. **Subscribe form** - Try valid and invalid inputs
2. **CSRF protection** - Submit form without CSRF token (should fail)
3. **Rate limiting** - Submit 20 times rapidly (should block)
4. **SQL injection** - Try `'; DROP TABLE subscribers--` (should be sanitized)
5. **XSS attack** - Try `<script>alert('xss')</script>` (should be escaped)
6. **Email validation** - Try `not-an-email` (should reject)
7. **Unsubscribe** - Test removal works
8. **Preview** - Check weather preview displays

---

## 🎉 You're Live!

Your secure web interface is now running! 🎊

**Access it at:** `http://192.168.1.198:5000`

Both services running:
- ✅ Email service (port N/A) - Scheduler & email monitoring
- ✅ Web interface (port 5000) - Subscription forms

---

*Last Updated: November 8, 2025*
