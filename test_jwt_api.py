"""
Test script for new JWT-protected API endpoints
Tests the structured data API for mobile apps
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_BASE_URL = "http://localhost:5001"
API_KEY = os.getenv('API_KEYS', '').split(',')[0] if os.getenv('API_KEYS') else None
TEST_EMAIL = "test@example.com"  # Change to your test user
TEST_PASSWORD = "testpassword123"  # Change to your test password

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_health_check():
    """Test the health check endpoint."""
    print_section("Testing Health Check")
    response = requests.get(f"{API_BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_authentication():
    """Test user authentication and get JWT token."""
    print_section("Testing Authentication (JWT Token)")
    
    if not API_KEY:
        print("❌ ERROR: API_KEY not configured!")
        return None
    
    headers = {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    data = {
        'email': TEST_EMAIL,
        'password': TEST_PASSWORD
    }
    
    response = requests.post(
        f"{API_BASE_URL}/api/users/authenticate",
        headers=headers,
        json=data
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        token = response.json().get('token')
        print(f"\n✅ JWT Token obtained: {token[:50]}...")
        return token
    else:
        print(f"\n❌ Authentication failed!")
        return None

def test_daily_brief(token):
    """Test the daily brief endpoint."""
    print_section("Testing Daily Brief (/api/v2/daily-brief)")
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    response = requests.get(
        f"{API_BASE_URL}/api/v2/daily-brief",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response (formatted):")
        print(json.dumps(data, indent=2))
        return True
    else:
        print(f"Error: {response.json()}")
        return False

def test_weather(token):
    """Test the weather endpoint."""
    print_section("Testing Weather Data (/api/v2/weather)")
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    response = requests.get(
        f"{API_BASE_URL}/api/v2/weather",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response (formatted):")
        print(json.dumps(data, indent=2))
        
        # Show week forecast summary
        if data.get('success') and data.get('data', {}).get('week_forecast'):
            print("\n📅 Week Forecast Summary:")
            for day in data['data']['week_forecast']:
                print(f"  {day['day_name']}: {day['temp_max']}°C / {day['temp_min']}°C - {day['condition']}")
        return True
    else:
        print(f"Error: {response.json()}")
        return False

def test_countdowns(token):
    """Test the countdowns endpoint."""
    print_section("Testing Countdowns (/api/v2/countdowns)")
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    response = requests.get(
        f"{API_BASE_URL}/api/v2/countdowns",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response (formatted):")
        print(json.dumps(data, indent=2))
        return True
    else:
        print(f"Error: {response.json()}")
        return False

def test_nameday(token):
    """Test the nameday endpoint."""
    print_section("Testing Nameday (/api/v2/nameday)")
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    response = requests.get(
        f"{API_BASE_URL}/api/v2/nameday",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response (formatted):")
        print(json.dumps(data, indent=2))
        return True
    else:
        print(f"Error: {response.json()}")
        return False

def test_invalid_token():
    """Test API with invalid token."""
    print_section("Testing Invalid Token (Security Check)")
    
    headers = {
        'Authorization': 'Bearer invalid_token_12345'
    }
    
    response = requests.get(
        f"{API_BASE_URL}/api/v2/daily-brief",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 401:
        print("✅ Correctly rejected invalid token")
        return True
    else:
        print("❌ Security issue: Invalid token was accepted!")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting API Tests for JWT-Protected Endpoints")
    print(f"📍 Base URL: {API_BASE_URL}")
    print(f"📧 Test User: {TEST_EMAIL}")
    
    results = {}
    
    # Test health check
    results['health'] = test_health_check()
    
    # Test authentication and get token
    token = test_authentication()
    
    if not token:
        print("\n❌ Cannot continue without valid JWT token")
        print("💡 Make sure:")
        print("   1. API server is running (python api.py)")
        print("   2. Test user exists in database")
        print("   3. API_KEYS is set in .env file")
        return
    
    # Test all data endpoints
    results['daily_brief'] = test_daily_brief(token)
    results['weather'] = test_weather(token)
    results['countdowns'] = test_countdowns(token)
    results['nameday'] = test_nameday(token)
    results['invalid_token'] = test_invalid_token()
    
    # Print summary
    print_section("Test Summary")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")

if __name__ == '__main__':
    main()
