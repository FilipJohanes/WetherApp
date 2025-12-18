#!/usr/bin/env python3
"""
Manual test script: Test web app subscription flow locally.
Uses Flask test client to simulate user interactions without running server.
"""
import os
import sys
import tempfile
from unittest.mock import patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import init_db



def mock_geocode(location):
    """Mock geocode function for testing."""
    locations = {
        'Bratislava, Slovakia': (48.1486, 17.1077, 'Bratislava, Slovakia', 'Europe/Bratislava'),
        'New York, USA': (40.7128, -74.0060, 'New York, USA', 'America/New_York'),
        'Tokyo, Japan': (35.6762, 139.6503, 'Tokyo, Japan', 'Asia/Tokyo'),
    }
    return locations.get(location, (50.0, 14.0, location, 'UTC'))


def mock_weather_forecast(lat, lon, timezone_str):
    """Mock weather forecast."""
    return {
        'temp_max': 22.0,
        'temp_min': 12.0,
        'precipitation_sum': 1.0,
        'precipitation_probability': 30,
        'wind_speed_max': 10.0,
    }


def test_web_flow():
    """Test complete web subscription flow."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║           Web App Subscription Flow Test                    ║
║           Testing Flask routes without server                ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # Create temporary test database
    fd, db_path = tempfile.mkstemp(suffix='_web_test.db')
    os.close(fd)
    os.environ['APP_DB_PATH'] = db_path
    
    print(f"🗄️  Test database: {db_path}\n")
    
    # Initialize database
    init_db(db_path)
    
    # Import after setting env var
    from web_app import app
    
    # Configure test client
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with patch('services.weather_service.geocode_location', side_effect=mock_geocode):
        with patch('services.weather_service.get_weather_forecast', side_effect=mock_weather_forecast):
            with app.test_client() as client:
                
                # Test 1: Home page
                print("📋 Test 1: Loading home page...")
                response = client.get('/')
                print(f"  ✅ Status: {response.status_code}")
                assert response.status_code == 200
                
                # Test 2: Subscribe page
                print("\n📋 Test 2: Loading subscribe page...")
                response = client.get('/subscribe')
                print(f"  ✅ Status: {response.status_code}")
                assert response.status_code == 200
                
                # Test 3: Subscribe new user
                print("\n📋 Test 3: Subscribing new user...")
                response = client.post('/subscribe?tab=weather', data={
                    'email': 'testuser@example.com',
                    'location': 'Bratislava, Slovakia',
                    'language': 'en',
                    'personality': 'neutral'
                }, follow_redirects=False)
                print(f"  ✅ Status: {response.status_code}")
                
                # Test 4: Preview page
                print("\n📋 Test 4: Loading preview page...")
                response = client.get('/preview?email=testuser@example.com')
                print(f"  ✅ Status: {response.status_code}")
                if response.status_code == 200:
                    print(f"  ✅ Preview generated successfully")
                
                # Test 5: Update existing subscription
                print("\n📋 Test 5: Updating subscription...")
                response = client.post('/subscribe?tab=weather', data={
                    'email': 'testuser@example.com',
                    'location': 'New York, USA',
                    'language': 'en',
                    'personality': 'cute'
                }, follow_redirects=False)
                print(f"  ✅ Status: {response.status_code}")
                
                # Test 6: Stats page
                print("\n📋 Test 6: Loading stats page...")
                response = client.get('/stats')
                print(f"  ✅ Status: {response.status_code}")
                assert response.status_code == 200
                
                # Test 7: API check-email
                print("\n📋 Test 7: Testing API check-email...")
                response = client.post('/api/check-email',
                    json={'email': 'testuser@example.com'}
                )
                print(f"  ✅ Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.get_json()
                    print(f"  ✅ Subscribed: {data.get('subscribed')}")
                    print(f"  ✅ Location: {data.get('location')}")
                
                # Test 8: Unsubscribe
                print("\n📋 Test 8: Unsubscribing user...")
                response = client.post('/unsubscribe', data={
                    'email': 'testuser@example.com'
                }, follow_redirects=True)
                print(f"  ✅ Status: {response.status_code}")
                
                # Test 9: Verify unsubscription
                print("\n📋 Test 9: Verifying unsubscription...")
                response = client.post('/api/check-email',
                    json={'email': 'testuser@example.com'}
                )
                if response.status_code == 200:
                    data = response.get_json()
                    print(f"  ✅ Subscribed: {data.get('subscribed')}")
    
    # Cleanup
    os.unlink(db_path)
    
    print(f"""
{'='*60}
✅ All web flow tests passed!
{'='*60}
""")


if __name__ == '__main__':
    test_web_flow()
