"""
API Client for Daily Brief Backend
Used by web_app.py to communicate with api.py backend
"""

import os
import requests
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

class BackendAPIClient:
    """Client for communicating with Daily Brief backend API."""
    
    def __init__(self):
        self.base_url = os.getenv('BACKEND_API_URL', 'http://localhost:5001')
        self.api_key = os.getenv('BACKEND_API_KEY', '')
        self.timeout = 10  # seconds
        
        if not self.api_key:
            raise ValueError("BACKEND_API_KEY environment variable not set")
    
    def _headers(self) -> Dict[str, str]:
        """Get request headers with API key."""
        return {
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def _get(self, endpoint: str) -> Optional[Dict]:
        """Make GET request to API."""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, headers=self._headers(), timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API GET error: {e}")
            return None
    
    def _post(self, endpoint: str, data: Dict) -> Optional[Dict]:
        """Make POST request to API."""
        response_data = None
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.post(url, json=data, headers=self._headers(), timeout=self.timeout)
            
            # Try to parse JSON response even on error
            try:
                response_data = response.json()
            except:
                response_data = None
            
            response.raise_for_status()
            return response_data
        except requests.exceptions.HTTPError as e:
            # HTTP error with response body
            print(f"API POST error: {e}")
            print(f"Response status: {response.status_code if 'response' in locals() else 'unknown'}")
            print(f"Response body: {response_data}")
            if response_data:
                return response_data  # Return error details from API
            return None
        except requests.exceptions.RequestException as e:
            # Connection error, timeout, etc.
            print(f"API POST error: {e}")
            return None
    
    def _put(self, endpoint: str, data: Dict) -> Optional[Dict]:
        """Make PUT request to API."""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.put(url, json=data, headers=self._headers(), timeout=self.timeout)
            
            # Try to parse JSON response even on error
            try:
                response_data = response.json()
            except:
                response_data = None
            
            response.raise_for_status()
            return response_data
        except requests.exceptions.HTTPError as e:
            # HTTP error with response body
            print(f"API PUT error: {e}")
            if response_data:
                return response_data  # Return error details from API
            return None
        except requests.exceptions.RequestException as e:
            # Connection error, timeout, etc.
            print(f"API PUT error: {e}")
            return None
    
    def _delete(self, endpoint: str) -> Optional[Dict]:
        """Make DELETE request to API."""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.delete(url, headers=self._headers(), timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API DELETE error: {e}")
            return None
    
    # ==================== USER METHODS ====================
    
    def register_user(self, email: str, password: str, nickname: str = None, 
                     username: str = None, email_consent: bool = False, 
                     terms_accepted: bool = False) -> tuple[bool, str]:
        """Register a new user."""
        data = {
            'email': email,
            'password': password,
            'nickname': nickname,
            'username': username,
            'email_consent': email_consent,
            'terms_accepted': terms_accepted
        }
        result = self._post('/api/users/register', data)
        if result and result.get('success'):
            return True, result.get('message', 'Registration successful')
        else:
            return False, result.get('error', 'Registration failed') if result else 'API connection failed'
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user data."""
        data = {'email': email, 'password': password}
        result = self._post('/api/users/authenticate', data)
        if result and result.get('success'):
            return result.get('user')
        return None
    
    def get_user(self, email: str) -> Optional[Dict]:
        """Get user data by email."""
        result = self._get(f'/api/users/{email}')
        if result and result.get('success'):
            return result.get('user')
        return None
    
    def update_password(self, email: str, new_password: str) -> bool:
        """Update user password."""
        data = {'new_password': new_password}
        result = self._put(f'/api/users/{email}/password', data)
        return result and result.get('success', False)
    
    def update_nickname(self, email: str, nickname: str) -> bool:
        """Update user nickname."""
        data = {'nickname': nickname}
        result = self._put(f'/api/users/{email}/nickname', data)
        return result and result.get('success', False)
    
    def request_password_reset(self, email: str) -> tuple[bool, str]:
        """Request a password reset email."""
        data = {'email': email}
        result = self._post('/api/users/password-reset-request', data)
        if result and result.get('success'):
            return True, result.get('message', 'Reset link sent if email exists')
        else:
            return False, result.get('error', 'Request failed') if result else 'API connection failed'
    
    def reset_password(self, token: str, new_password: str) -> tuple[bool, str]:
        """Reset password using token."""
        data = {'token': token, 'new_password': new_password}
        result = self._post('/api/users/password-reset', data)
        if result and result.get('success'):
            return True, result.get('message', 'Password reset successful')
        else:
            return False, result.get('error', 'Reset failed') if result else 'API connection failed'
    
    # ==================== WEATHER SUBSCRIPTION METHODS ====================
    
    def get_weather_subscription(self, email: str) -> Optional[Dict]:
        """Get weather subscription for user."""
        result = self._get(f'/api/weather/subscriptions/{email}')
        if result and result.get('success'):
            return result.get('subscription')
        return None
    
    def create_weather_subscription(self, email: str, location: str, 
                                   personality: str = 'neutral', 
                                   language: str = 'en') -> tuple[bool, str]:
        """Create or update weather subscription."""
        data = {
            'email': email,
            'location': location,
            'personality': personality,
            'language': language
        }
        result = self._post('/api/weather/subscriptions', data)
        if result and result.get('success'):
            return True, result.get('location', location)
        else:
            return False, result.get('error', 'Subscription failed') if result else 'API connection failed'
    
    def update_weather_subscription(self, email: str, location: str, 
                                   personality: str, language: str) -> bool:
        """Update weather subscription."""
        success, _ = self.create_weather_subscription(email, location, personality, language)
        return success
    
    def delete_weather_subscription(self, email: str) -> bool:
        """Delete weather subscription."""
        result = self._delete(f'/api/weather/subscriptions/{email}')
        return result and result.get('success', False)
    
    def preview_weather(self, email: str) -> Optional[Dict]:
        """Get weather preview for user."""
        result = self._get(f'/api/weather/preview/{email}')
        if result and result.get('success'):
            return {
                'subscriber': result.get('subscriber'),
                'weather_summary': result.get('weather_summary')
            }
        return None
    
    # ==================== COUNTDOWN METHODS ====================
    
    def get_countdowns(self, email: str) -> List[Dict]:
        """Get all countdowns for user."""
        result = self._get(f'/api/countdowns/{email}')
        if result and result.get('success'):
            return result.get('countdowns', [])
        return []
    
    def create_countdown(self, email: str, name: str, date: str, 
                        yearly: bool = False, message_before: str = '', 
                        message_after: str = '') -> tuple[bool, str]:
        """Create a new countdown. Returns (success, message)."""
        data = {
            'email': email,
            'name': name,
            'date': date,
            'yearly': yearly,
            'message_before': message_before,
            'message_after': message_after
        }
        result = self._post('/api/countdowns', data)
        if result and result.get('success'):
            return True, result.get('message', 'Countdown created')
        return False, result.get('error', 'Failed to create countdown') if result else 'API connection failed'
    
    def update_countdown(self, countdown_id: int, name: str, date: str, 
                        yearly: bool = False, message_before: str = '') -> bool:
        """Update countdown."""
        data = {
            'name': name,
            'date': date,
            'yearly': yearly,
            'message_before': message_before
        }
        result = self._put(f'/api/countdowns/{countdown_id}', data)
        return result and result.get('success', False)
    
    def delete_countdown(self, countdown_id: int) -> bool:
        """Delete countdown."""
        result = self._delete(f'/api/countdowns/{countdown_id}')
        return result and result.get('success', False)
    
    # ==================== STATS METHODS ====================
    
    def get_stats(self) -> Optional[Dict]:
        """Get public statistics."""
        result = self._get('/api/stats')
        if result and result.get('success'):
            return {
                'total': result.get('total_subscribers', 0),
                'languages': result.get('languages', []),
                'personalities': result.get('personalities', [])
            }
        return None


# Singleton instance
_api_client = None

def get_api_client() -> BackendAPIClient:
    """Get or create API client singleton."""
    global _api_client
    if _api_client is None:
        _api_client = BackendAPIClient()
    return _api_client
