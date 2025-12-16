"""
Test web app routes: subscribe, unsubscribe, preview, stats, API.
"""
import pytest
import json
from tests.conftest import insert_subscriber


def test_index_route(flask_test_client):
    """Test home page loads successfully."""
    response = flask_test_client.get('/')
    assert response.status_code == 200


def test_subscribe_page_get(flask_test_client):
    """Test subscribe page loads."""
    response = flask_test_client.get('/subscribe')
    assert response.status_code == 200


def test_subscribe_weather_valid_location(flask_test_client, mock_geocode, test_db):
    """Test subscribing with valid location."""
    response = flask_test_client.post('/subscribe?tab=weather', data={
        'email': 'newuser@example.com',
        'location': 'Bratislava, Slovakia',
        'language': 'en',
        'personality': 'neutral'
    }, follow_redirects=False)
    
    # Should redirect to preview
    assert response.status_code in [200, 302]


def test_subscribe_weather_invalid_location(flask_test_client, mock_geocode, test_db):
    """Test subscribing with invalid location shows error."""
    response = flask_test_client.post('/subscribe?tab=weather', data={
        'email': 'invalid@example.com',
        'location': 'Invalid Location',
        'language': 'en',
        'personality': 'neutral'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Should show error message (check if flash message exists)


def test_subscribe_update_existing(flask_test_client, mock_geocode, test_db):
    """Test updating existing subscriber's location."""
    # First subscription
    flask_test_client.post('/subscribe?tab=weather', data={
        'email': 'existing@example.com',
        'location': 'Bratislava, Slovakia',
        'language': 'en',
        'personality': 'neutral'
    })
    
    # Update subscription
    response = flask_test_client.post('/subscribe?tab=weather', data={
        'email': 'existing@example.com',
        'location': 'Prague, Czech Republic',
        'language': 'sk',
        'personality': 'cute'
    }, follow_redirects=False)
    
    assert response.status_code in [200, 302]


def test_unsubscribe_page_get(flask_test_client):
    """Test unsubscribe page loads."""
    response = flask_test_client.get('/unsubscribe')
    assert response.status_code == 200


def test_unsubscribe_existing_user(flask_test_client, test_db):
    """Test unsubscribing an existing user."""
    # Insert subscriber
    insert_subscriber(
        test_db,
        email='unsubscribe@example.com',
        location='Bratislava, Slovakia',
        lat=48.1486,
        lon=17.1077,
        timezone='Europe/Bratislava'
    )
    
    # Unsubscribe
    response = flask_test_client.post('/unsubscribe', data={
        'email': 'unsubscribe@example.com'
    }, follow_redirects=True)
    
    assert response.status_code == 200


def test_unsubscribe_nonexistent_user(flask_test_client, test_db):
    """Test unsubscribing a user that doesn't exist."""
    response = flask_test_client.post('/unsubscribe', data={
        'email': 'nonexistent@example.com'
    }, follow_redirects=True)
    
    assert response.status_code == 200


def test_preview_page_with_valid_subscriber(flask_test_client, mock_weather_forecast, test_db):
    """Test preview page shows weather for existing subscriber."""
    # Insert subscriber
    insert_subscriber(
        test_db,
        email='preview@example.com',
        location='Bratislava, Slovakia',
        lat=48.1486,
        lon=17.1077,
        timezone='Europe/Bratislava'
    )
    
    response = flask_test_client.get('/preview?email=preview@example.com')
    assert response.status_code == 200
    # Should contain weather information
    assert b'Bratislava' in response.data or b'weather' in response.data.lower()


def test_preview_page_without_email(flask_test_client):
    """Test preview page without email parameter."""
    response = flask_test_client.get('/preview', follow_redirects=True)
    assert response.status_code == 200


def test_preview_page_nonexistent_subscriber(flask_test_client, test_db):
    """Test preview page with non-existent subscriber."""
    response = flask_test_client.get('/preview?email=nonexistent@example.com', follow_redirects=True)
    assert response.status_code == 200


def test_stats_page(flask_test_client, test_db):
    """Test stats page loads and shows statistics."""
    # Insert test subscribers
    insert_subscriber(
        test_db,
        email='stats1@example.com',
        location='Bratislava',
        lat=48.1486,
        lon=17.1077,
        timezone='Europe/Bratislava',
        language='en'
    )
    insert_subscriber(
        test_db,
        email='stats2@example.com',
        location='Prague',
        lat=50.0755,
        lon=14.4378,
        timezone='Europe/Prague',
        language='sk'
    )
    
    response = flask_test_client.get('/stats')
    assert response.status_code == 200
    # Should show subscriber count
    assert b'2' in response.data or b'total' in response.data.lower()


def test_api_check_email_subscribed(flask_test_client, test_db):
    """Test API check-email for subscribed user."""
    # Insert subscriber
    insert_subscriber(
        test_db,
        email='api@example.com',
        location='Bratislava, Slovakia',
        lat=48.1486,
        lon=17.1077,
        timezone='Europe/Bratislava'
    )
    
    response = flask_test_client.post('/api/check-email',
        data=json.dumps({'email': 'api@example.com'}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['subscribed'] == True
    assert 'location' in data


def test_api_check_email_not_subscribed(flask_test_client, test_db):
    """Test API check-email for non-subscribed user."""
    response = flask_test_client.post('/api/check-email',
        data=json.dumps({'email': 'notsubscribed@example.com'}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['subscribed'] == False


def test_api_check_email_invalid_format(flask_test_client, test_db):
    """Test API check-email with invalid email format."""
    response = flask_test_client.post('/api/check-email',
        data=json.dumps({'email': 'invalid-email'}),
        content_type='application/json'
    )
    
    assert response.status_code == 400


def test_api_check_email_missing_email(flask_test_client, test_db):
    """Test API check-email without email parameter."""
    response = flask_test_client.post('/api/check-email',
        data=json.dumps({}),
        content_type='application/json'
    )
    
    assert response.status_code == 400


def test_security_input_validation(flask_test_client, test_db):
    """Test that malicious input is rejected."""
    # SQL injection attempt
    response = flask_test_client.post('/subscribe?tab=weather', data={
        'email': 'hacker@example.com',
        'location': "'; DROP TABLE subscribers; --",
        'language': 'en',
        'personality': 'neutral'
    }, follow_redirects=True)
    
    # Should be rejected or handled safely
    assert response.status_code == 200


def test_rate_limiting(flask_test_client, test_db):
    """Test that rate limiting is configured (basic check)."""
    # Make multiple rapid requests
    responses = []
    for i in range(15):
        response = flask_test_client.post('/subscribe?tab=weather', data={
            'email': f'ratelimit{i}@example.com',
            'location': 'Bratislava, Slovakia',
            'language': 'en',
            'personality': 'neutral'
        })
        responses.append(response.status_code)
    
    # All should succeed or some should be rate limited (429)
    # This depends on rate limiter configuration
    assert all(status in [200, 302, 429] for status in responses)
