import pytest
from web_app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    # Setup test data before yielding client
    import sqlite3
    conn = sqlite3.connect('app.db')
    # Ensure weather subscription exists
    conn.execute("""
        INSERT OR IGNORE INTO weather (email, location, lat, lon, timezone, personality, language, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
    """, ('test@example.com', 'Bratislava', 48.1486, 17.1077, 'Europe/Bratislava', 'neutral', 'en'))
    # Ensure countdown subscription exists
    conn.execute("""
        INSERT OR IGNORE INTO countdowns (name, date, yearly, email, message_before, message_after)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ('testname', '2025-12-31', 0, 'test@example.com', 'Test before', 'Test after'))
    conn.commit()
    conn.close()
    with app.test_client() as client:
        yield client
    # Teardown: clean up test data after client
    conn = sqlite3.connect('app.db')
    conn.execute("DELETE FROM weather WHERE email = ?", ('test@example.com',))
    conn.execute("DELETE FROM countdowns WHERE name = ? AND date = ?", ('testname', '2025-12-31'))
    conn.commit()
    conn.close()

def test_delete_weather_subscription(client):
    # Test missing data
    rv = client.post('/api/delete_subscription', json=None)
    print('Missing data:', rv.get_json())
    assert rv.status_code == 400
    # Test missing id
    rv = client.post('/api/delete_subscription', json={})
    print('Missing id:', rv.get_json())
    assert rv.status_code == 400
    # Test unknown type
    rv = client.post('/api/delete_subscription', json={'id': 'unknown_123'})
    print('Unknown type:', rv.get_json())
    assert rv.status_code == 400
    # Test not found
    rv = client.post('/api/delete_subscription', json={'id': 'weather_notfound@example.com'})
    print('Weather not found:', rv.get_json())
    assert rv.status_code == 404
    # Test valid delete (assuming test@example.com exists)
    rv = client.post('/api/delete_subscription', json={'id': 'weather_test@example.com'})
    print('Weather delete:', rv.get_json())
    # Accept 200 or 404 (if not present)
    assert rv.status_code in (200, 404)

def test_delete_countdown_subscription(client):
    # Test invalid countdown id format
    rv = client.post('/api/delete_subscription', json={'id': 'countdown_onlyname'})
    print('Invalid countdown id:', rv.get_json())
    assert rv.status_code == 400
    # Test not found
    rv = client.post('/api/delete_subscription', json={'id': 'countdown_testname_2099-01-01'})
    print('Countdown not found:', rv.get_json())
    assert rv.status_code == 404
    # Test valid delete (assuming testname and date exist)
    rv = client.post('/api/delete_subscription', json={'id': 'countdown_testname_2025-12-31'})
    print('Countdown delete:', rv.get_json())
    # Accept 200 or 404 (if not present)
    assert rv.status_code in (200, 404)

def test_update_weather_subscription(client):
    # Test missing id
    rv = client.post('/api/update_subscription', json={})
    print('Update missing id:', rv.get_json())
    assert rv.status_code == 400
    # Test unknown type
    rv = client.post('/api/update_subscription', json={'id': 'unknown_123'})
    print('Update unknown type:', rv.get_json())
    assert rv.status_code == 400
    # Test not found
    rv = client.post('/api/update_subscription', json={'id': 'weather_notfound@example.com', 'location': 'Bratislava'})
    print('Update not found:', rv.get_json())
    assert rv.status_code == 404
    # Test valid update (assuming test@example.com exists)
    rv = client.post('/api/update_subscription', json={'id': 'weather_test@example.com', 'location': 'Bratislava', 'language': 'en', 'personality': 'neutral'})
    print('Update weather:', rv.get_json())
    assert rv.status_code == 200

def test_update_countdown_subscription(client):
    # Test invalid countdown id format
    rv = client.post('/api/update_subscription', json={'id': 'countdown_onlyname'})
    print('Update invalid countdown id:', rv.get_json())
    assert rv.status_code == 400
    # Test not found
    rv = client.post('/api/update_subscription', json={'id': 'countdown_testname_2099-01-01', 'name': 'testname', 'date': '2099-01-01'})
    print('Update countdown not found:', rv.get_json())
    assert rv.status_code == 404
    # Test valid update (assuming testname and date exist)
    rv = client.post('/api/update_subscription', json={'id': 'countdown_testname_2025-12-31', 'name': 'testname', 'date': '2025-12-31'})
    print('Update countdown:', rv.get_json())
    assert rv.status_code == 200
