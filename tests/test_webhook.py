#!/usr/bin/env python3
"""
Test webhook service connectivity
"""

import requests
import json

def test_webhook_service():
    """Test all webhook endpoints"""
    base_url = "http://localhost:5002"
    
    tests = [
        ("GET", "/health", None),
        ("GET", "/stats", None),
        ("POST", "/webhook/test", None),
        ("POST", "/webhook/email", {
            "from": "test@example.com",
            "subject": "Prague, Czech Republic", 
            "body": "Subscribe me to weather updates",
            "message_id": "test123"
        })
    ]
    
    for method, endpoint, data in tests:
        url = f"{base_url}{endpoint}"
        print(f"\n🧪 Testing {method} {url}")
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=5)
            else:
                response = requests.post(url, json=data, timeout=5)
            
            print(f"✅ Status: {response.status_code}")
            print(f"📄 Response: {response.text[:200]}...")
            
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection refused - service not accessible")
        except requests.exceptions.Timeout:
            print(f"❌ Timeout - service not responding")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_webhook_service()