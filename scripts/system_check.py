#!/usr/bin/env python3
"""
Comprehensive System Check
Validates all components are working correctly
"""
import os
import sys
from pathlib import Path

print("=" * 70)
print("DAILY BRIEF SYSTEM CHECK")
print("=" * 70)
print()

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

issues = []
warnings = []

# 1. Check Python version
print("1️⃣  Python Version Check")
print("-" * 70)
import sys
py_version = sys.version_info
if py_version.major == 3 and py_version.minor >= 9:
    print(f"✅ Python {py_version.major}.{py_version.minor}.{py_version.micro}")
else:
    issues.append(f"Python version {py_version.major}.{py_version.minor} - requires 3.9+")
    print(f"❌ Python {py_version.major}.{py_version.minor} - requires 3.9+")
print()

# 2. Check required packages
print("2️⃣  Required Packages Check")
print("-" * 70)
required_packages = {
    'requests': 'requests',
    'flask': 'Flask',
    'flask_wtf': 'Flask-WTF',
    'flask_limiter': 'Flask-Limiter',
    'bcrypt': 'bcrypt',
    'jwt': 'PyJWT',
    'dotenv': 'python-dotenv',
    'email_validator': 'email-validator',
    'dateutil': 'python-dateutil',
    'apscheduler': 'APScheduler',
    'timezonefinder': 'timezonefinder',
}

for module_name, package_name in required_packages.items():
    try:
        __import__(module_name)
        print(f"✅ {package_name}")
    except ImportError:
        issues.append(f"Missing package: {package_name}")
        print(f"❌ {package_name} - NOT INSTALLED")
print()

# 3. Check environment variables
print("3️⃣  Environment Variables Check")
print("-" * 70)
required_vars = ['EMAIL_ADDRESS', 'EMAIL_PASSWORD', 'SMTP_HOST']
optional_vars = ['API_KEYS', 'BACKEND_API_KEY', 'WEB_APP_URL', 'JWT_SECRET_KEY', 'FLASK_SECRET_KEY']

for var in required_vars:
    value = os.getenv(var)
    if value:
        print(f"✅ {var}: {'*' * min(len(value), 10)}")
    else:
        issues.append(f"Missing required environment variable: {var}")
        print(f"❌ {var}: NOT SET")

for var in optional_vars:
    value = os.getenv(var)
    if value:
        print(f"✅ {var}: {'*' * min(len(value), 10)}")
    else:
        warnings.append(f"Optional variable not set: {var}")
        print(f"⚠️  {var}: NOT SET")
print()

# 4. Check database path
print("4️⃣  Database Configuration Check")
print("-" * 70)
db_path = os.getenv("APP_DB_PATH", "app.db")
print(f"Database path: {db_path}")

if os.path.exists(db_path):
    print(f"✅ Database file exists")
    
    # Check database schema
    import sqlite3
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['users', 'weather_subscriptions', 'countdowns', 'password_reset_tokens']
        for table in required_tables:
            if table in tables:
                print(f"✅ Table '{table}' exists")
            else:
                issues.append(f"Missing database table: {table}")
                print(f"❌ Table '{table}' missing")
        
        # Check users table schema
        cursor = conn.execute("PRAGMA table_info(users)")
        user_columns = [row[1] for row in cursor.fetchall()]
        
        if 'lat' in user_columns or 'lon' in user_columns:
            issues.append("Users table has lat/lon columns (should be removed)")
            print(f"❌ Users table has lat/lon columns (run migration!)")
        else:
            print(f"✅ Users table schema correct (no lat/lon)")
        
        conn.close()
    except Exception as e:
        issues.append(f"Database error: {e}")
        print(f"❌ Database error: {e}")
else:
    warnings.append(f"Database file not found: {db_path}")
    print(f"⚠️  Database file not found (will be created on first use)")
print()

# 5. Check service imports
print("5️⃣  Service Modules Check")
print("-" * 70)
services = [
    'services.user_service',
    'services.subscription_service',
    'services.countdown_service',
    'services.weather_service',
    'services.email_service',
    'services.namedays_service',
    'services.api_service',
]

for service in services:
    try:
        __import__(service)
        print(f"✅ {service}")
    except Exception as e:
        issues.append(f"Cannot import {service}: {e}")
        print(f"❌ {service}: {e}")
print()

# 6. Check API/Web files
print("6️⃣  Main Application Files Check")
print("-" * 70)
main_files = {
    'api.py': 'Backend API',
    'web_app.py': 'Web Frontend',
    'api_client.py': 'API Client',
}

for file, desc in main_files.items():
    if os.path.exists(file):
        print(f"✅ {desc} ({file})")
    else:
        issues.append(f"Missing file: {file}")
        print(f"❌ {desc} ({file}) - NOT FOUND")
print()

# Summary
print("=" * 70)
print("SUMMARY")
print("=" * 70)

if not issues and not warnings:
    print("✅ ALL CHECKS PASSED - System is ready!")
elif not issues and warnings:
    print(f"✅ System is operational with {len(warnings)} warnings")
    print("\nWarnings:")
    for warning in warnings:
        print(f"  ⚠️  {warning}")
else:
    print(f"❌ Found {len(issues)} critical issues:")
    for issue in issues:
        print(f"  ❌ {issue}")
    if warnings:
        print(f"\nAlso {len(warnings)} warnings:")
        for warning in warnings:
            print(f"  ⚠️  {warning}")

print()
print("=" * 70)
sys.exit(0 if not issues else 1)
