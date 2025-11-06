# 📋 Quick Email Setup Checklist

## 🎯 **What You Need to Do (15 minutes)**

### **Step 1: Create Service Email (5 minutes)**
- [ ] Go to Gmail.com → "Create account"
- [ ] Choose username like: `yourname-dailybrief@gmail.com`
- [ ] Write down the email and password

### **Step 2: Enable App Password (5 minutes)**
- [ ] Go to: https://myaccount.google.com/security
- [ ] Enable "2-Step Verification" (use your phone)
- [ ] Go to: https://myaccount.google.com/apppasswords
- [ ] Create app password for "Mail" → "Daily Brief Service"
- [ ] **COPY THE 16-CHARACTER PASSWORD** (looks like: `abcd efgh ijkl mnop`)

### **Step 3: Configure Service (3 minutes)**
- [ ] Copy `.env.example` to `.env` in your project folder
- [ ] Edit `.env` file with your settings:

```env
EMAIL_ADDRESS=your-dailybrief@gmail.com
EMAIL_PASSWORD=abcd efgh ijkl mnop
IMAP_HOST=imap.gmail.com
SMTP_HOST=smtp.gmail.com
```

### **Step 4: Test (2 minutes)**
- [ ] Run: `python app.py --send-test your-personal@gmail.com`
- [ ] Check your personal email for test message

---

## 🚨 **Important Notes**

⚠️ **USE APP PASSWORD, NOT REGULAR PASSWORD!**
- Gmail requires 16-character app password
- Regular Gmail password will NOT work
- You must enable 2FA first

⚠️ **Keep Credentials Safe:**
- Don't share the app password
- Don't commit `.env` to git (already in .gitignore)

---

## 📧 **Email Suggestions**

Good service email names:
- `yourname-weather@gmail.com`
- `family-assistant@gmail.com`
- `yourname-dailybrief@gmail.com`
- `home-automation@gmail.com`

---

## 🧪 **Testing Your Setup**

Once configured, test by sending emails to your service:

**Weather Subscription Test:**
```
From: your-personal@gmail.com
To: your-service@gmail.com
Subject: Weather Test
Body: London
```

**Calendar Reminder Test:**
```
From: your-personal@gmail.com  
To: your-service@gmail.com
Subject: Reminder Test
Body: date=tomorrow
time=2pm
message=Test reminder
```

**Slovak Language Test:**
```
From: your-personal@gmail.com
To: your-service@gmail.com
Subject: Slovak Test
Body: Bratislava
personality=neutral
language=sk
```

---

## ✅ **Ready to Deploy?**

After email setup:
1. **Local testing:** Run `python app.py --dry-run`
2. **Pi Zero 2 W:** Upload and run service 24/7
3. **Alpha testing:** Share service email with friends/family

**You're 15 minutes away from having your own personal weather assistant! 🌤️💕**