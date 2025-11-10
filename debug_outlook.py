import imaplib
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

email = os.getenv("EMAIL_ADDRESS")
password = os.getenv("EMAIL_PASSWORD")
imap_host = os.getenv("IMAP_HOST")
imap_port = int(os.getenv("IMAP_PORT", "993"))

print("="*60)
print("DETAILED OUTLOOK IMAP DEBUG TEST")
print("="*60)
print(f"Email: {email}")
print(f"Password length: {len(password)} characters")
print(f"Password starts with: {password[:8]}...")
print(f"Password ends with: ...{password[-8:]}")
print(f"IMAP Host: {imap_host}")
print(f"IMAP Port: {imap_port}")
print()

# Test different approaches
print("🔍 Testing multiple authentication methods:")
print()

# Method 1: Standard IMAP4_SSL
print("1️⃣ Testing standard IMAP4_SSL connection:")
try:
    mail = imaplib.IMAP4_SSL(imap_host, imap_port)
    print("   ✅ Connected to IMAP server")
    
    # Enable debugging to see raw IMAP conversation
    mail.debug = 4
    print("   📝 Attempting login with full debugging...")
    
    response = mail.login(email, password)
    print(f"   ✅ Login successful: {response}")
    mail.logout()
    print("   ✅ Method 1 SUCCESS!")
    
except Exception as e:
    print(f"   ❌ Method 1 failed: {e}")
    print()

# Method 2: Try with explicit AUTH=PLAIN
print("2️⃣ Testing IMAP with AUTH=PLAIN:")
try:
    mail = imaplib.IMAP4_SSL(imap_host, imap_port)
    print("   ✅ Connected to IMAP server")
    
    # Try authenticate method instead of login
    import base64
    auth_string = f'\0{email}\0{password}'
    auth_string_b64 = base64.b64encode(auth_string.encode()).decode()
    
    # Send AUTHENTICATE PLAIN command
    response = mail.authenticate('PLAIN', lambda x: auth_string_b64)
    print(f"   ✅ AUTH PLAIN successful: {response}")
    mail.logout()
    print("   ✅ Method 2 SUCCESS!")
    
except Exception as e:
    print(f"   ❌ Method 2 failed: {e}")
    print()

# Method 3: Check capabilities
print("3️⃣ Checking server capabilities:")
try:
    mail = imaplib.IMAP4_SSL(imap_host, imap_port)
    print("   ✅ Connected to IMAP server")
    
    # Check what authentication methods are supported
    response = mail.capability()
    print(f"   📋 Server capabilities: {response}")
    
    mail.logout()
    
except Exception as e:
    print(f"   ❌ Method 3 failed: {e}")

print()
print("="*60)
print("DEBUG COMPLETE")
print("="*60)