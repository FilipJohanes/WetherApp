# 🧪 Test Suite

Comprehensive test suite for the Daily Brief Service covering all functionality.

## Test Files Overview

### **Core Functionality**
- `test_daily_brief.py` - Main service integration tests
- `test_weather.py` - Weather API and geocoding tests  
- `test_daily_job.py` - Scheduled job testing

### **Localization Testing** 🌍
- `test_localization.py` - Complete localization system testing
- `test_localization_safe.py` - Safe dry-run localization tests
- `preview_emuska.py` - Preview Slovak emuska emails (no sending)
- `test_weather_loading.py` - Weather message file loading tests

### **Language & Personality Testing**
- `test_personality_language.py` - Personality modes and language switching
- `test_multilang.py` - Multi-language message generation
- `test_emuska.py` - Emuska personality mode specifics
- `test_princess.py` - Princess/cute mode testing
- `test_slovak_email.py` - Slovak email testing (dry run)

### **Slovak Language Specific** 🇸🇰
- `test_slovak.py` - Basic Slovak functionality
- `test_slovak_complete.py` - Comprehensive Slovak testing
- `test_integration_sk.py` - Slovak integration tests

### **Advanced Features**  
- `test_webhook.py` - Webhook architecture testing
- `test_calendar_reminders.py` - Calendar system tests (disabled)
- `test_messages_comprehensive.py` - Message formatting tests

### **Test Runners**
- `test_all.py` - Run complete test suite

## Running Tests

```bash
# Interactive test runner (recommended) 
python tests/test_runner.py

# Run all tests
python tests/test_all.py

# Run specific test
python tests/test_weather.py

# Run with pytest (if installed)
pytest tests/
```

## Test Status
- ✅ Weather Service: Fully tested
- ✅ Multi-language: Comprehensive coverage  
- ✅ Personality Modes: All 4 modes tested
- ❌ Reminder System: Disabled (tests preserved)

Total: **14 test files** covering all active functionality.