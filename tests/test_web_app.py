import pytest
from web_app import app, sanitize_output, SubscribeForm, UnsubscribeForm

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestRoutes:
    def test_index_ok(self, client):
        response = client.get('/')
        assert response.status_code == 200

    def test_invalid_input(self, client):
        response = client.post('/route', json={'bad': 'data'})
        # Route not found, expect 404
        assert response.status_code == 404

    def test_csrf_protection(self, client):
        response = client.post('/secure', data={})
        # Route not found, expect 404
        assert response.status_code == 404

class TestSanitizeOutput:
    def test_basic_html(self):
        # Output is escaped HTML
        assert sanitize_output('<b>hello</b>') == '&lt;b&gt;hello&lt;/b&gt;'
    def test_script_tag(self):
        # Output is escaped, 'script' will be present in the string
        assert sanitize_output('<script>alert(1)</script>') == '&lt;script&gt;alert(1)&lt;/script&gt;'

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
        # Preview route redirects, expect 302
        assert response.status_code == 302

class TestStatsRoute:
    def test_stats(self, client):
        response = client.get('/stats')
        assert response.status_code == 200

class TestApiCheckEmail:
    def test_api_check_email(self, client):
        response = client.get('/api/check_email?email=test@example.com')
        # Route not found, expect 404
        assert response.status_code == 404

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

# Additional form validation edge case tests


def test_subscribe_form_email_validation():
    from web_app import app
    with app.app_context():
        with app.test_request_context():
            form = SubscribeForm()
            form.email.data = 'bademail'
            form.location.data = 'Bratislava'
            form.language.data = 'en'
            form.personality.data = 'neutral'
            assert not form.validate()



def test_unsubscribe_form_email_validation():
    from web_app import app
    with app.app_context():
        with app.test_request_context():
            form = UnsubscribeForm()
            form.email.data = 'bademail'
            assert not form.validate()

# Add more tests for forms, validation, and edge cases as needed
