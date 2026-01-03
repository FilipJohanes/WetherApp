#!/usr/bin/env python3
"""
Test Password Reset Functionality
Run this after starting api.py to verify password reset works
"""

import requests
import json
import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = "http://localhost:5001"
API_KEY = os.getenv('API_KEYS', '').split(',')[0]

print("🔐 Testing Password Reset Functionality\n")
print(f"API URL: {API_BASE_URL}")
print(f"API Key: {API_KEY[:10]}...\n")

headers = {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
}

# Step 1: Create a test user
print("=" * 60)
print("Step 1: Creating test user")
print("=" * 60)

test_email = "password_reset_test@example.com"
test_password = "OldPassword123!"

register_data = {
    'email': test_email,
    'password': test_password,
    'nickname': 'Test User',
    'username': '',
    'email_consent': True,
    'terms_accepted': True
}

try:
    response = requests.post(f"{API_BASE_URL}/api/users/register", headers=headers, json=register_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Note: {e}")

# Step 2: Request password reset
print("\n" + "=" * 60)
print("Step 2: Requesting password reset")
print("=" * 60)

reset_request_data = {'email': test_email}

try:
    response = requests.post(f"{API_BASE_URL}/api/users/password-reset-request", headers=headers, json=reset_request_data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    if response.status_code == 200:
        print("\n✅ Password reset email would be sent (check email service logs)")
except Exception as e:
    print(f"❌ Error: {e}")

# Step 3: Get the token from database
print("\n" + "=" * 60)
print("Step 3: Retrieving reset token from database")
print("=" * 60)

db_path = os.getenv("APP_DB_PATH", "app.db")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

try:
    token_row = conn.execute("""
        SELECT token, email, expires_at, used 
        FROM password_reset_tokens 
        WHERE email = ? AND used = 0
        ORDER BY created_at DESC LIMIT 1
    """, (test_email,)).fetchone()
    
    if token_row:
        token = token_row['token']
        print(f"Token found: {token[:20]}...")
        print(f"Email: {token_row['email']}")
        print(f"Expires: {token_row['expires_at']}")
        print(f"Used: {token_row['used']}")
        
        # Step 4: Reset password using token
        print("\n" + "=" * 60)
        print("Step 4: Resetting password with token")
        print("=" * 60)
        
        new_password = "NewPassword456!"
        reset_data = {
            'token': token,
            'new_password': new_password
        }
        
        try:
            response = requests.post(f"{API_BASE_URL}/api/users/password-reset", headers=headers, json=reset_data)
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 200:
                print("\n✅ Password reset successful!")
                
                # Step 5: Test login with new password
                print("\n" + "=" * 60)
                print("Step 5: Testing login with new password")
                print("=" * 60)
                
                login_data = {'email': test_email, 'password': new_password}
                response = requests.post(f"{API_BASE_URL}/api/users/authenticate", headers=headers, json=login_data)
                print(f"Status: {response.status_code}")
                print(f"Response: {json.dumps(response.json(), indent=2)}")
                
                if response.status_code == 200:
                    print("\n✅ Login with new password successful!")
                else:
                    print("\n❌ Login with new password failed!")
            else:
                print("\n❌ Password reset failed!")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("❌ No token found in database")
        
except Exception as e:
    print(f"❌ Database error: {e}")
finally:
    conn.close()

# Cleanup
print("\n" + "=" * 60)
print("Cleanup: Deleting test user")
print("=" * 60)

conn = sqlite3.connect(db_path)
try:
    conn.execute("DELETE FROM users WHERE email = ?", (test_email,))
    conn.execute("DELETE FROM password_reset_tokens WHERE email = ?", (test_email,))
    conn.commit()
    print(f"✅ Test user {test_email} deleted")
except Exception as e:
    print(f"❌ Cleanup error: {e}")
finally:
    conn.close()

print("\n" + "=" * 60)
print("✅ Password Reset Test Complete!")
print("=" * 60)
