#!/usr/bin/env python3
"""
Send daily emails to all users in app.db immediately (force send mode)
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import Config, load_env
from services.email_service import run_daily_job

def main():
    print("=" * 60)
    print("🚀 FORCE SENDING DAILY EMAILS TO ALL USERS")
    print("=" * 60)
    print()
    
    # Load configuration
    try:
        config = load_env()
        print(f"✅ Configuration loaded")
        print(f"   From: {config.email_address}")
        print(f"   Timezone: {config.timezone}")
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return False
    
    # Database path
    db_path = os.path.join(os.path.dirname(__file__), '..', 'app.db')
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    print(f"✅ Database: {db_path}")
    print()
    print("📤 Sending emails to all users (bypassing time check)...")
    print("=" * 60)
    print()
    
    # Run daily job with force_send=True to bypass time check
    try:
        run_daily_job(config, dry_run=False, db_path=db_path, force_send=True)
        print()
        print("=" * 60)
        print("✅ Daily job completed!")
        print("=" * 60)
        return True
    except Exception as e:
        print(f"❌ Error running daily job: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
