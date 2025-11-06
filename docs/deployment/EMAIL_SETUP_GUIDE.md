# 📧 Email Setup Guide for Daily Brief Service

## 🎯 **Step 1: Create Dedicated Service Email**

### **Why You Need a Dedicated Email:**
- ✅ **Security**: Keep your personal email separate
- ✅ **Organization**: All service emails in one place  
- ✅ **App Passwords**: Easier to manage dedicated credentials
- ✅ **Monitoring**: Clear separation of service vs personal emails

### **Recommended Email Providers:**

## 🥇 **Option 1: Gmail (Recommended)**

### **Create Gmail Account:**
1. **Go to:** https://accounts.google.com/signup
2. **Username suggestions:**
   - `your-name-dailybrief@gmail.com`
   - `your-name-weatherbot@gmail.com`
   - `family-assistant-2024@gmail.com`
3. **Use strong password** (you'll create app password later)

### **Enable App Password (Required):**
```
⚠️ IMPORTANT: Gmail requires "App Passwords" for external apps
You cannot use your regular Gmail password!
```

**Setup Steps:**
1. **Enable 2-Factor Authentication:**
   - Go to: https://myaccount.google.com/security
   - Click "2-Step Verification" → Turn On
   - Use your phone number for verification

2. **Create App Password:**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (custom name)"
   - Enter: "Daily Brief Service"
   - **Copy the 16-character password** (save this!)

3. **Gmail Settings:**
   ```
   EMAIL_ADDRESS=your-service-email@gmail.com
   EMAIL_PASSWORD=abcd efgh ijkl mnop  # 16-char app password
   IMAP_HOST=imap.gmail.com
   SMTP_HOST=smtp.gmail.com
   IMAP_PORT=993
   SMTP_PORT=587
   SMTP_USE_TLS=true
   ```

## 🥈 **Option 2: Outlook/Hotmail**

### **Create Outlook Account:**
1. **Go to:** https://outlook.live.com
2. **Click:** "Create free account"
3. **Choose:** @outlook.com or @hotmail.com

### **Enable App Password:**
1. **Go to:** https://account.microsoft.com/security
2. **Click:** "Advanced security options"
3. **Turn on:** "Two-step verification"
4. **Create:** App password for "Mail"

### **Outlook Settings:**
```
EMAIL_ADDRESS=your-service@outlook.com
EMAIL_PASSWORD=your-app-password
IMAP_HOST=outlook.office365.com
SMTP_HOST=smtp.office365.com
IMAP_PORT=993
SMTP_PORT=587
SMTP_USE_TLS=true
```

## 🥉 **Option 3: Yahoo Mail**

### **Create Yahoo Account:**
1. **Go to:** https://login.yahoo.com/account/create
2. **Create account** with unique name

### **Enable App Password:**
1. **Go to:** Yahoo Account Security
2. **Turn on:** Two-step verification
3. **Generate:** App password for "Desktop app"

### **Yahoo Settings:**
```
EMAIL_ADDRESS=your-service@yahoo.com
EMAIL_PASSWORD=your-app-password
IMAP_HOST=imap.mail.yahoo.com
SMTP_HOST=smtp.mail.yahoo.com
IMAP_PORT=993
SMTP_PORT=587
SMTP_USE_TLS=true
```

---

## 🛠️ **Step 2: Configure Your Service**

### **Create .env File:**
```bash
# In your reminderAPP directory
cp .env.example .env
nano .env  # or notepad .env on Windows
```

### **Fill in Your Settings:**
```env
# === REQUIRED EMAIL SETTINGS ===
EMAIL_ADDRESS=your-dailybrief@gmail.com
EMAIL_PASSWORD=your-16-char-app-password
IMAP_HOST=imap.gmail.com
SMTP_HOST=smtp.gmail.com

# === OPTIONAL SETTINGS ===
IMAP_PORT=993
SMTP_PORT=587
SMTP_USE_TLS=true
TZ=Europe/Bratislava
LANGUAGE=en
```

---

## 🧪 **Step 3: Test Configuration**

### **Test Email Sending:**
```bash
# Test if you can send emails
python app.py --send-test your-personal-email@gmail.com
```

**Expected output:**
```
✅ Email sent successfully to your-personal-email@gmail.com
```

### **Test Email Receiving:**
```bash
# Test if you can receive commands
# Send email TO your service account:
# From: your-personal-email@gmail.com
# To: your-dailybrief@gmail.com
# Subject: Test
# Body: London

# Then run:
python app.py --dry-run
```

---

## 📋 **Step 4: Service Email Best Practices**

### **Email Account Security:**
- ✅ **Use strong password** for the email account
- ✅ **Enable 2FA** (required for app passwords)
- ✅ **Use app passwords** (never regular passwords)
- ✅ **Don't share credentials** 

### **Service Configuration:**
- ✅ **Set clear email signature** explaining it's automated
- ✅ **Configure auto-reply** explaining service usage
- ✅ **Keep inbox organized** (service will mark emails as read)

### **Example Auto-Reply Message:**
```
This is an automated Daily Brief Service.

Send commands:
- Location name (e.g., "London") for weather subscription
- "delete" to unsubscribe
- Calendar: date=tomorrow, time=2pm, message=Meeting

For help: Reply with "help"
```

---

## 🚨 **Troubleshooting Common Issues**

### **"Authentication Failed" Error:**
```
❌ Problem: IMAP/SMTP login failed
✅ Solution: 
  1. Double-check app password (not regular password)
  2. Verify 2FA is enabled
  3. Check IMAP/SMTP settings match provider
```

### **"Connection Timeout" Error:**
```
❌ Problem: Can't connect to email server
✅ Solution:
  1. Check internet connection
  2. Verify IMAP/SMTP hosts are correct
  3. Check firewall isn't blocking ports 993/587
```

### **"Less Secure Apps" Error:**
```
❌ Problem: Gmail blocking connection
✅ Solution:
  1. Use App Password (not regular password)
  2. Enable 2FA first
  3. Don't use "Less secure apps" option
```

---

## 📧 **Email Configuration Templates**

Copy and paste into your `.env` file:

### **Gmail Template:**
```env
EMAIL_ADDRESS=your-service@gmail.com
EMAIL_PASSWORD=abcd efgh ijkl mnop
IMAP_HOST=imap.gmail.com
SMTP_HOST=smtp.gmail.com
IMAP_PORT=993
SMTP_PORT=587
SMTP_USE_TLS=true
TZ=Europe/Bratislava
```

### **Outlook Template:**
```env
EMAIL_ADDRESS=your-service@outlook.com
EMAIL_PASSWORD=your-app-password
IMAP_HOST=outlook.office365.com
SMTP_HOST=smtp.office365.com
IMAP_PORT=993
SMTP_PORT=587
SMTP_USE_TLS=true
TZ=Europe/Bratislava
```

---

## ✅ **Email Setup Checklist**

- [ ] Created dedicated service email account
- [ ] Enabled 2-Factor Authentication  
- [ ] Generated app password (16 characters)
- [ ] Copied .env.example to .env
- [ ] Filled in email credentials in .env
- [ ] Tested sending: `python app.py --send-test your-email@example.com`
- [ ] Tested receiving: Send test email and run `python app.py --dry-run`
- [ ] Configured auto-reply message (optional)

---

## 🎉 **You're Ready!**

Once you complete this email setup, your Daily Brief Service will be able to:
- ✅ **Receive commands** via email (weather subscriptions, reminders)
- ✅ **Send responses** (confirmations, weather reports)
- ✅ **Process automatically** (24/7 monitoring)

**Next step:** Deploy on your Pi Zero 2 W or test locally! 🚀