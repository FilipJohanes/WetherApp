#!/usr/bin/env python3
"""
Database Schema Validator
Validates that all database operations use correct columns
"""
import sqlite3
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def validate_schema():
    """Validate database schema matches code expectations."""
    db_path = os.getenv("APP_DB_PATH", "app.db")
    
    print("=" * 70)
    print("DATABASE SCHEMA VALIDATION")
    print("=" * 70)
    print(f"Database: {db_path}")
    print()
    
    if not os.path.exists(db_path):
        print(f"⚠️  Database not found: {db_path}")
        print("   This is expected if database hasn't been initialized yet.")
        return True
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    try:
        # Expected schema
        expected_schema = {
            'users': [
                'email',  # PRIMARY KEY
                'username',
                'nickname',
                'password_hash',
                'timezone',
                'subscription_type',
                'weather_enabled',
                'countdown_enabled',
                'reminder_enabled',
                'email_consent',
                'terms_accepted',
                'created_at',
                'updated_at'
            ],
            'weather_subscriptions': [
                'email',  # PRIMARY KEY, FOREIGN KEY
                'location',
                'lat',
                'lon',
                'personality',
                'language',
                'last_sent_date',
                'updated_at'
            ],
            'countdowns': [
                'id',  # PRIMARY KEY AUTOINCREMENT
                'email',  # FOREIGN KEY
                'name',
                'date',
                'yearly',
                'message_before',
                'message_after',
                'created_at'
            ],
            'password_reset_tokens': [
                'id',  # PRIMARY KEY AUTOINCREMENT
                'email',
                'token',
                'created_at',
                'expires_at',
                'used'
            ]
        }
        
        all_valid = True
        
        for table_name, expected_columns in expected_schema.items():
            print(f"📋 {table_name.upper()} TABLE")
            print("-" * 70)
            
            # Check if table exists
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """, (table_name,))
            
            if not cursor.fetchone():
                print(f"   ❌ Table does not exist!")
                all_valid = False
                print()
                continue
            
            # Get actual columns
            cursor = conn.execute(f"PRAGMA table_info({table_name})")
            actual_columns = [row[1] for row in cursor.fetchall()]
            
            # Compare
            missing = set(expected_columns) - set(actual_columns)
            extra = set(actual_columns) - set(expected_columns)
            
            if not missing and not extra:
                print(f"   ✅ Schema matches expectations")
                print(f"   Columns: {', '.join(actual_columns)}")
            else:
                if missing:
                    print(f"   ❌ Missing columns: {', '.join(missing)}")
                    all_valid = False
                if extra:
                    print(f"   ⚠️  Extra columns: {', '.join(extra)}")
                    print(f"      (These may be from old schema and should be removed)")
                    all_valid = False
                print(f"   Actual columns: {', '.join(actual_columns)}")
            
            # Count records
            count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            print(f"   Records: {count}")
            print()
        
        # Check for problematic columns that were removed
        print("🔍 CHECKING FOR REMOVED COLUMNS")
        print("-" * 70)
        
        removed_columns = {
            'users': ['lat', 'lon', 'id', 'personality', 'reset_token', 'reset_token_expiry', 'mfa_secret', 'status']
        }
        
        for table_name, should_not_exist in removed_columns.items():
            cursor = conn.execute(f"PRAGMA table_info({table_name})")
            actual_columns = [row[1] for row in cursor.fetchall()]
            
            found_removed = [col for col in should_not_exist if col in actual_columns]
            if found_removed:
                print(f"   ⚠️  {table_name}: Found columns that should be removed: {', '.join(found_removed)}")
                print(f"      Run: python scripts/migrate_remove_user_latlon.py")
                all_valid = False
            else:
                print(f"   ✅ {table_name}: No problematic columns found")
        
        print()
        print("=" * 70)
        if all_valid:
            print("✅ DATABASE SCHEMA IS VALID")
        else:
            print("❌ DATABASE SCHEMA HAS ISSUES - SEE ABOVE")
        print("=" * 70)
        
        return all_valid
        
    finally:
        conn.close()

if __name__ == "__main__":
    success = validate_schema()
    sys.exit(0 if success else 1)
