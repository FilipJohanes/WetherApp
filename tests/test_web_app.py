import pytest
from web_app import create_app, sanitize_output

@pytest.fixture
def flask_app():
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(flask_app):
    return flask_app.test_client()

class TestRoutes:
    def test_index_ok(self, client):
        response = client.get('/')
        assert response.status_code == 200

    def test_invalid_input(self, client):
        response = client.post('/route', json={'bad': 'data'})
        assert response.status_code in (400, 422)

    def test_csrf_protection(self, client):
        response = client.post('/secure', data={})
        assert response.status_code in (403, 400)

class TestSanitizeOutput:
    def test_basic_html(self):
        assert sanitize_output('<b>hello</b>') == 'hello'
    def test_script_tag(self):
        assert 'script' not in sanitize_output('<script>alert(1)</script>')

class TestIndexRoute:
    def test_index_route(self, client):
        response = client.get('/')
        assert response.status_code == 200
        assert b"Subscribe" in response.data

class TestSubscribeRoute:
    def test_subscribe_get(self, client):
        response = client.get('/subscribe')
        assert response.status_code == 200
    def test_subscribe_post_invalid(self, client):
        response = client.post('/subscribe', data={"email": "bad", "location": ""})
        assert response.status_code in (400, 422)

class TestUnsubscribeRoute:
    def test_unsubscribe_get(self, client):
        response = client.get('/unsubscribe')
        assert response.status_code == 200
    def test_unsubscribe_post_invalid(self, client):
        response = client.post('/unsubscribe', data={"email": "bad"})
        assert response.status_code in (400, 422)

class TestPreviewRoute:
    def test_preview(self, client):
        response = client.get('/preview')
        assert response.status_code == 200

class TestStatsRoute:
    def test_stats(self, client):
        response = client.get('/stats')
        assert response.status_code == 200

class TestApiCheckEmail:
    def test_api_check_email(self, client):
        response = client.get('/api/check_email?email=test@example.com')
        assert response.status_code == 200

class TestErrorHandlers:
    def test_404(self, client):
        response = client.get('/not-a-real-route')
        assert response.status_code == 404
    def test_500(self, client):
        # Simulate internal error if possible
        pass

class TestSecurityHeaders:
    def test_security_headers(self, client):
        response = client.get('/')
        assert 'X-Content-Type-Options' in response.headers
        assert 'X-Frame-Options' in response.headers

# Add more tests for forms, validation, and edge cases as needed
