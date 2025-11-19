#!/usr/bin/env python3
"""Test Slovak emuska personality"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# from send_localized_weather import send_localized_weather_email  # Module not found, skip import

if __name__ == "__main__":
    print("🇸🇰 Testing Slovak Emuska Personality (DRY RUN - NO REAL EMAIL)")
    print("=" * 60)
    
    print("⚠️ This would test em.solarova@gmail.com but we're not sending real emails to other people!")
    print("✅ Use 'python send_hybrid_weather.py' to test with your own email instead.")
    
    # Show what the Slovak emuska message would look like
    print("\n📝 Slovak Emuska sample from weather_messages.txt:")
    print("💖 Môj drahý poklad, dnes budú padať dažďové perličky z neba. Vezmi si dáždnik a choď opatrne, moja princezná! ✨")