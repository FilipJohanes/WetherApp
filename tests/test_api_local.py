#!/usr/bin/env python3
"""
Local API Testing Script
Test the API endpoints locally to debug issues.
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_BASE_URL = "http://localhost:5001"  # Local API
# API_BASE_URL = "http://dailyweather.duckdns.org:5001"  # Remote API

# Get API key from environment
API_KEY = os.getenv('API_KEYS', '').split(',')[0] if os.getenv('API_KEYS') else None

if not API_KEY:
    print("❌ No API_KEY found in .env file!")
    print("Add API_KEYS=your_key_here to your .env file")
    exit(1)

print(f"✅ Using API Key: {API_KEY[:10]}...")
print(f"🌐 Testing API at: {API_BASE_URL}\n")


def test_health():
    """Test health check endpoint."""
    print("=" * 50)
    print("Testing Health Check")
    print("=" * 50)
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_register(email, password, nickname="Test User"):
    """Test user registration."""
    print("\n" + "=" * 50)
    print("Testing User Registration")
    print("=" * 50)
    
    headers = {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    data = {
        'email': email,
        'password': password,
        'nickname': nickname,
        'username': '',
        'email_consent': True,
        'terms_accepted': True
    }
    
    print(f"Request URL: {API_BASE_URL}/api/users/register")
    print(f"Headers: {headers}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/users/register",
            headers=headers,
            json=data,
            timeout=10
        )
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_login(email, password):
    """Test user login."""
    print("\n" + "=" * 50)
    print("Testing User Login")
    print("=" * 50)
    
    headers = {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    data = {
        'email': email,
        'password': password
    }
    
    print(f"Request URL: {API_BASE_URL}/api/users/authenticate")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/users/authenticate",
            headers=headers,
            json=data,
            timeout=10
        )
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run API tests."""
    print("\n🧪 Starting API Tests\n")
    
    # Test 1: Health check
    health_ok = test_health()
    
    if not health_ok:
        print("\n❌ Health check failed! Is the API running?")
        print("\nTo start the API locally, run:")
        print("  python api.py")
        return
    
    # Test 2: Register a test user
    test_email = f"test_{os.urandom(4).hex()}@example.com"
    test_password = "TestPassword123!"
    
    register_ok = test_register(test_email, test_password, "Test User")
    
    # Test 3: Login with the test user
    if register_ok:
        test_login(test_email, test_password)
    
    print("\n" + "=" * 50)
    print("Tests Complete")
    print("=" * 50)


if __name__ == "__main__":
    main()
