# 📖 Daily Brief Service - User Manual

## 🌟 Welcome to Your Personal Weather Assistant!

Your Daily Brief Service is an intelligent email-driven assistant that provides:
- 🌤️ **Daily Weather Updates** with personality
- 📅 **Smart Calendar Reminders** 
- 💕 **Multi-Language Support** including romantic Slovak princess mode

---

## 📧 **Getting Started**

### **Service Email Address**
```
dailywether.reminder@gmail.com
```

### **How It Works**
1. **Send emails** to the service address with simple commands
2. **Receive instant responses** confirming your requests
3. **Get daily weather** delivered at 05:00 local time
4. **Receive reminders** exactly when scheduled

---

## 🌤️ **Weather Subscriptions**

### **Basic Weather Subscription**
```
To: dailywether.reminder@gmail.com
Subject: Weather Subscription
Body: London
```
**Result:** Daily weather reports for London at 05:00

### **Personality Modes** 🎭
Choose how your weather assistant talks to you:

#### **Neutral Mode** (Default)
```
Body: Prague
personality=neutral
```
**Example:** "Take an umbrella - it's going to rain today."

#### **Cute Mode** 💕
```
Body: New York
personality=cute
```  
**Example:** "🌧️ Pitter-patter raindrops are coming! Don't forget your cute umbrella! ☂️"

#### **Brutal Mode** 😤
```
Body: Berlin
personality=brutal
```
**Example:** "Rain incoming. Umbrella or get soaked. Your choice."

### **Multi-Language Support** 🌍

#### **English** (Default)
```
Body: London
language=en
personality=cute
```

#### **Spanish**
```
Body: Madrid  
language=es
personality=brutal
```

#### **Slovak**
```
Body: Bratislava
language=sk
personality=neutral
```

---

## 📅 **Calendar Reminders**

### **Basic Reminder**
```
To: dailywether.reminder@gmail.com
Subject: Reminder
Body: date=tomorrow
time=2pm
message=Team meeting in conference room
```

### **Advanced Date Formats**
```
date=2024-12-25          # Christmas
date=next Friday         # Natural language
date=in 3 days          # Relative dates
time=14:30              # 24-hour format
time=2:30pm             # 12-hour format
```

### **Reminder Examples**

#### **Doctor Appointment**
```
Body: date=next Tuesday
time=10am
message=Doctor appointment - bring insurance card
```

#### **Birthday Reminder**
```
Body: date=2024-11-15
time=9am
message=Mom's birthday - call her!
```

#### **Meeting Reminder**
```
Body: date=tomorrow
time=14:00
message=Project review meeting via Teams
```

---

## 🛠️ **Management Commands**

### **Change Personality Mode**
```
Body: personality=cute
```
Updates your weather reports to cute mode.

### **Change Language**
```
Body: language=es
```
Switches to Spanish weather reports.

### **Unsubscribe from Weather**
```
Body: delete
```
Stops daily weather emails.

### **Get Help**
```
Body: help
```
Receive this user manual via email.

---

## 📬 **Sample Daily Weather Report**

### **English Cute Mode**
```
Subject: Today's Weather for London

Today's weather for London:

🌡️ Temperature: High 18°C / Low 12°C
🌧️ Rain probability: 70% (≈3.0 mm)
💨 Wind: up to 15 km/h

💡 🌧️ Pitter-patter raindrops are coming! Don't forget your cute umbrella! ☂️

👕 Fashion advice: Wear light jacket or sweater, rain jacket, waterproof shoes and look absolutely adorable! 💖
```

---

## 🌍 **Supported Languages & Personalities**

| Language | Neutral | Cute | Brutal |
|----------|---------|------|---------|
| **English (en)** | ✅ | ✅ | ✅ |
| **Spanish (es)** | ✅ | ✅ | ✅ |
| **Slovak (sk)** | ✅ | ✅ | ✅ |

---

## 📍 **Supported Locations**

### **Major Cities** (Just use city name)
- London, Paris, Berlin, Rome
- New York, Los Angeles, Chicago  
- Tokyo, Sydney, Mumbai
- Prague, Bratislava, Vienna

### **Specific Locations** (Be more specific)
```
Prague, Czech Republic
New York, NY
Los Angeles, CA
London, UK
```

### **Coordinates** (Advanced users)
```
48.1486,17.1077    # Bratislava coordinates
```

---

## ⏰ **Service Schedule**

- **Daily Weather:** 05:00 local time (Bratislava timezone)
- **Email Monitoring:** Every minute
- **Reminder Delivery:** Exact time specified
- **Response Time:** Usually within 1 minute

---

## 💡 **Tips & Tricks**

### **For Best Results:**
- ✅ **Use clear location names** (e.g., "Prague, CZ" vs just "Prague")
- ✅ **One command per email** for clarity
- ✅ **Check spam folder** for service responses
- ✅ **Use specific times** for reminders (e.g., "2:30pm" vs "afternoon")

### **Personality Mode Tips:**
- **Neutral:** Professional weather reports
- **Cute:** Fun, emoji-rich weather with playful language
- **Brutal:** Direct, no-nonsense weather facts


### **Multi-Language Setup:**
```
# Complete Slovak princess setup
Body: Bratislava
personality=emuska
language=sk

# Spanish brutal mode
Body: Madrid
personality=brutal
language=es
```

---

## 🚨 **Troubleshooting**

### **Not Receiving Weather Reports?**
1. **Check spam folder** - automated emails sometimes go there
2. **Verify subscription** - send your location again
3. **Wait until next 05:00** - daily delivery time

### **Commands Not Working?**
1. **Check email format** - use exact syntax from examples
2. **One command per email** - don't mix weather and reminders
3. **Reply from same email** - service recognizes your email address

### **Personality Mode Issues?**
- **Emuska only works in Slovak** - other languages fall back to cute mode
- **Case sensitive** - use lowercase: `personality=cute` not `Personality=Cute`

### **Location Not Found?**
```
# Instead of: "Prague"
# Try: "Prague, Czech Republic"
# Or: "Prague, CZ" 
```

---

## 🎯 **Quick Reference Commands**

### **Weather Subscriptions**
```
London                              # Basic subscription
Prague\npersonality=cute           # Cute weather reports  
Madrid\nlanguage=es                # Spanish language
Bratislava\npersonality=neutral\nlanguage=sk  # Slovak language
```

### **Calendar Reminders**
```
date=tomorrow\ntime=2pm\nmessage=Meeting    # Tomorrow at 2pm
date=next Friday\ntime=9am\nmessage=Call   # Next Friday at 9am
```

### **Management**
```
delete                             # Unsubscribe weather
personality=brutal                 # Change personality  
language=sk                       # Change language
help                              # Get help
```

---

## 📞 **Support**

### **Need Help?**
- **Email:** Send "help" to `dailywether.reminder@gmail.com`
- **Status Check:** Send "status" for subscription information

### **Feature Requests**
Want new languages, personalities, or features? Let us know!

---

## 🗄️ Database Structure

The Daily Brief Service uses a single SQLite database (`app.db`) with multiple tables to manage users, subscriptions, weather, reminders, countdowns, and email logs. Here is the current structure:

### **users** (master table)
- `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- `email` (TEXT, UNIQUE, NOT NULL)
- `active` (INTEGER, default 1)
- `weather_enabled` (INTEGER, default 0)
- `countdown_enabled` (INTEGER, default 0)
- `reminder_enabled` (INTEGER, default 0)
- `timezone` (TEXT, default 'UTC')
- `last_active` (TEXT)
- `created_at` (TEXT)
- `personality` (TEXT, default 'neutral')
- `language` (TEXT, default 'en')

### **weather**
- `email` (TEXT, PRIMARY KEY)
- `location` (TEXT)
- `lat` (REAL)
- `lon` (REAL)
- `updated_at` (TEXT)
- `personality` (TEXT, default 'neutral')
- `language` (TEXT, default 'en')
- `timezone` (TEXT, default 'UTC')
- `last_sent_date` (TEXT)
- `countdown_enabled` (INTEGER, default 0)
- `reminder_enabled` (INTEGER, default 0)

### **reminders**
- `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- `email` (TEXT)
- `message` (TEXT)
- `first_run_at` (TEXT)
- `remaining_repeats` (INTEGER)
- `last_sent_at` (TEXT)
- `created_at` (TEXT)

### **countdowns**
- `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- `email` (TEXT)
- `name` (TEXT)
- `date` (TEXT)
- `yearly` (INTEGER)
- `message_before` (TEXT)
- `message_after` (TEXT)

### **inbox_log**
- `uid` (TEXT, PRIMARY KEY)
- `from_email` (TEXT)
- `received_at` (TEXT)
- `subject` (TEXT)
- `body_hash` (TEXT)

---
#

This structure allows efficient management of users and their subscriptions, weather data, reminders, countdowns, and email logs. The master `users` table provides quick access to user status and subscription flags, minimizing unnecessary database queries.

For more details or schema changes, see the developer documentation or contact support.

---

## 🎉 **Welcome to Your Daily Brief Service!**

Enjoy your personalized weather assistant with personality! Whether you prefer professional reports, cute messages, or brutal honesty - we've got you covered! 🌤️

**Happy weather watching! ☀️🌧️❄️**