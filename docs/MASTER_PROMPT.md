# 🚀 Daily Brief Service - Master Development Prompt

## 📋 **Project Context & Continuation Guide**

This document provides the complete context and development approach for the **Daily Brief Service** project, enabling seamless continuation with GitHub Copilot on any development environment.

---

## 🎯 **Project Overview**

**Daily Brief Service** is a proprietary, production-ready email-driven weather service with unique multi-language personality features.

### **Core Features:**
- 📧 **Email-driven architecture**: Control via email commands
- 🌍 **3-language support**: English, Spanish, Slovak
- 🎭 **4 personality modes**: neutral, cute, brutal, **emuska** (unique Slovak)
- 🌤️ **Daily weather delivery**: Automated at 5:00 AM
- 🛡️ **Production-ready**: Signal handling, Unicode support, error recovery
- 🧪 **Comprehensive testing**: Interactive test suite with safe mode

### **Unique Intellectual Property:**
- **Slovak "emuska" personality**: Original custom messages like "💖 Môj žiarivý diamant, slnko svieti práve pre teba!"
- **Hybrid localization system**: Preserves original weather messages while adding system message translations
- **Email processing architecture**: Smart parsing with system email filtering

---

## 🔧 **Development Philosophy & Approach**

### **1. Code Quality Standards:**
```
- Always prioritize clean, organized project structure
- Use proper directory organization (tests/, scripts/, examples/, docs/)
- Never create files in root directory without checking for appropriate subdirectory
- Include comprehensive error handling and logging
- Add type hints and documentation for complex functions
- Use emojis in user-facing messages for friendly experience
```

### **2. Project Organization Principles:**
```
c:\Projects\reminderAPP\
├── 📧 Core Service Files (root level only)
│   ├── app.py (main service)
│   ├── localization.py (3-language system)
│   ├── daily_brief.db (SQLite database)
│   ├── .env (configuration)
│   ├── LICENSE (proprietary)
│   ├── README.md & requirements.txt
├── 🌍 languages/ (localization content)
├── 🧪 tests/ (all testing files)
├── 🔧 scripts/ (utilities & database tools)
├── 📋 examples/ (configs & demos)
├── 📚 docs/ (documentation)
└── 🌐 webhook/ (scalability features)
```

### **3. Localization Architecture:**
- **System messages**: Located in `languages/{lang}/messages.txt`
- **Weather messages**: Located in `languages/{lang}/weather_messages.txt`
- **Hybrid approach**: Preserve original content while adding translations
- **Slovak emuska**: Special personality with custom romantic messages

### **4. Development Workflow:**
```bash
# Always follow this Git workflow:
git add .                    # Stage changes
git commit -m "description"  # Descriptive commit with emojis
git push origin main         # Push to GitHub

# Before creating new files, check for appropriate directory
# Fix import paths when moving files between directories
# Update README files when adding to directories
```

---

## 🎭 **Personality System Details**

### **Language Support:**
- **English (EN)**: `neutral`, `cute`, `brutal`
- **Spanish (ES)**: `neutral`, `cute`, `brutal`  
- **Slovak (SK)**: `neutral`, `cute`, `brutal`, **`emuska`**

### **Slovak Emuska Personality (Crown Jewel):**
**This is our unique intellectual property - handle with special care:**

```
Examples of emuska messages:
☀️ "Môj žiarivý diamant, slnko svieti práve pre teba! Vyjdi von a zažiar ako kráľovná."
🌧️ "Môj drahý poklad, dnes budú padať dažďové perličky z neba. Vezmi si dáždnik a choď opatrne, moja princezná!"
❄️ "Zlatíčko moje, vonku tancujú nádherné snehové víly! Oblieč si najteplejší kabátik!"
```

**Characteristics:**
- Romantic, caring, protective tone
- Uses diminutives: "zlatíčko", "srdiečko", "pampúšik"
- Addresses user as royalty: "princezná", "kráľovná", "diamant"
- Includes protective advice with emotional warmth
- Heavy use of heart and diamond emojis (💖💎✨)

---

## 🛠️ **Technical Architecture**

### **Core Components:**
1. **app.py**: Main service with APScheduler, email monitoring, signal handling
2. **localization.py**: LocalizationManager with fallback systems
3. **Database**: SQLite with subscribers, reminders (disabled), inbox_log tables
4. **Email System**: Gmail IMAP/SMTP with Unicode-safe logging
5. **Weather API**: Open-Meteo with geocoding (no API keys required)

### **Key Technical Decisions:**
- **Hybrid message system**: Keep original weather_messages.txt, add system message translations
- **Email safety**: Filter system emails, only send test emails to main developer
- **Signal handling**: Graceful shutdown with Ctrl+C support
- **Unicode logging**: SafeStreamHandler for international character support
- **Proprietary licensing**: Strict protection of intellectual property

### **Configuration:**
```env
EMAIL_ADDRESS=dailywether.reminder@gmail.com
EMAIL_PASSWORD=mxkz epiv xwxj zotq
IMAP_HOST=imap.gmail.com
SMTP_HOST=smtp.gmail.com
TZ=Europe/Bratislava
```

---

## 🧪 **Testing Environment**

### **Interactive Testing:**
```bash
# Main test runner (located in tests/)
python tests/test_runner.py

# Key testing commands:
E - Preview emuska messages (most important for personality testing)
L - Localization tests (safe, no emails)
W - Weather API tests
A - Run all safe tests
```

### **Email Safety Protocols:**
- **Production email**: `dailywether.reminder@gmail.com`
- **Test emails only go to**: `filip.johanes9@gmail.com`
- **Never send test emails to**: `em.solarova@gmail.com` or other real users
- **Use dry-run mode** for most testing scenarios

---

## 🔒 **Legal & Intellectual Property**

### **License Status:**
- **Type**: Proprietary (NOT open source)
- **Commercial use**: PROHIBITED without licensing
- **Redistribution**: PROHIBITED
- **Personal use**: Allowed
- **Contact for licensing**: filip.johanes9@gmail.com

### **Protected Assets:**
- Slovak emuska personality messages (original creative content)
- Multi-language localization architecture
- Email processing algorithms
- Hybrid message system design

---

## 💡 **Development Guidelines for Copilot**

### **When Adding New Features:**
1. **Check directory structure** before creating files
2. **Preserve Slovak emuska content** - never modify original messages
3. **Add comprehensive error handling** with user-friendly messages
4. **Include logging** with appropriate emoji indicators
5. **Update relevant README files** when adding to directories
6. **Test email functionality** safely (only to main developer)
7. **Maintain backwards compatibility** with existing database

### **Communication Style:**
- Use emojis in commit messages and user-facing text
- Write descriptive commit messages explaining the "why"
- Be enthusiastic about Slovak emuska personality features
- Maintain professional tone while being friendly
- Acknowledge unique features as "intellectual property"

### **Code Organization Rules:**
```
✅ DO:
- Use appropriate subdirectories for new files
- Fix import paths when moving files
- Add type hints for complex functions
- Include comprehensive error handling
- Test changes thoroughly before committing

❌ DON'T:
- Create files in root directory without checking for subdirectory
- Modify original Slovak emuska messages
- Send test emails to real users (except main developer)
- Remove existing functionality without discussion
- Make breaking changes to database schema
```

---

## 🚀 **Quick Start for New Environment**

### **1. Clone and Setup:**
```bash
git clone https://github.com/FilipJohanes/WetherApp.git
cd WetherApp
pip install -r requirements.txt
cp examples/.env.example .env
# Edit .env with email credentials
```

### **2. Run Service:**
```bash
python app.py  # Start main service
# Press Ctrl+C to stop gracefully
```

### **3. Test Environment:**
```bash
python tests/test_runner.py  # Interactive testing
```

### **4. Development Workflow:**
```bash
# Create feature branch (optional)
git checkout -b feature-name

# Make changes (following directory guidelines)
# Test changes
python tests/test_runner.py

# Commit and push
git add .
git commit -m "✨ Description with emoji"
git push origin main
```

---

## 📞 **Contact & Licensing**

**Developer**: Filip Johanes  
**Email**: filip.johanes9@gmail.com  
**Repository**: https://github.com/FilipJohanes/WetherApp  
**License**: Proprietary - Commercial licensing available

---

## 🌟 **Project Philosophy**

This project represents a perfect blend of:
- **Technical Excellence**: Clean architecture, comprehensive testing, production-ready features
- **Cultural Appreciation**: Authentic Slovak language support with unique personality
- **User Experience**: Friendly, emoji-rich communication with multiple personality options
- **Professional Standards**: Proper licensing, documentation, and development practices

**The Slovak emuska personality is our crown jewel** - treat it as precious intellectual property that makes this service truly unique in the market.

---

*This master prompt should be used as the foundation for all future development work on the Daily Brief Service project. It captures not just the technical details, but the philosophy, approach, and special considerations that make this project successful.*