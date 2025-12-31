#!/usr/bin/env python3
"""
Quick test script to verify API separation works
Run this after starting api.py to test the connection
"""

import os
import sys

# Test if we can import the API client
try:
    from api_client import get_api_client
    print("✅ API client module imported successfully")
except ImportError as e:
    print(f"❌ Failed to import api_client: {e}")
    sys.exit(1)

# Check environment variables
required_vars = ['BACKEND_API_URL', 'BACKEND_API_KEY']
missing = [var for var in required_vars if not os.getenv(var)]

if missing:
    print(f"❌ Missing environment variables: {', '.join(missing)}")
    print("Create a .env file with:")
    print("  BACKEND_API_URL=http://localhost:5001")
    print("  BACKEND_API_KEY=<your-api-key>")
    sys.exit(1)

print(f"✅ Environment variables configured")
print(f"   API URL: {os.getenv('BACKEND_API_URL')}")

# Try to initialize client
try:
    client = get_api_client()
    print(f"✅ API client initialized: {client.base_url}")
except Exception as e:
    print(f"❌ Failed to initialize API client: {e}")
    sys.exit(1)

# Test health endpoint
print("\n🔍 Testing backend connection...")
import requests

try:
    response = requests.get(f"{client.base_url}/health", timeout=5)
    if response.status_code == 200:
        print("✅ Backend API is responding!")
        print(f"   Response: {response.json()}")
    else:
        print(f"❌ Backend returned status {response.status_code}")
        sys.exit(1)
except requests.exceptions.ConnectionError:
    print(f"❌ Cannot connect to backend at {client.base_url}")
    print("   Make sure api.py is running!")
    sys.exit(1)
except Exception as e:
    print(f"❌ Connection error: {e}")
    sys.exit(1)

# Test authenticated endpoint
print("\n🔍 Testing API authentication...")
try:
    stats = client.get_stats()
    if stats:
        print("✅ API authentication working!")
        print(f"   Total subscribers: {stats.get('total', 0)}")
    else:
        print("⚠️  Could not fetch stats (might be normal if DB is empty)")
except Exception as e:
    print(f"❌ API authentication failed: {e}")
    print("   Check that BACKEND_API_KEY matches the API server")
    sys.exit(1)

print("\n✅ All tests passed! API separation is working correctly.")
print("\nNext steps:")
print("1. Start app.py for the backend scheduler")
print("2. Keep api.py running for API requests")
print("3. Start web_app.py for the frontend (or deploy to Railway)")
