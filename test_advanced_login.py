#!/usr/bin/env python3
"""
Advanced Outlook IMAP login test with different authentication methods
"""
import imaplib
import os
import ssl
from dotenv import load_dotenv

load_dotenv()

email = os.getenv("EMAIL_ADDRESS")
password = os.getenv("EMAIL_PASSWORD")

def test_with_different_auth_methods():
    """Test different authentication approaches for Outlook"""
    
    print("🧪 TESTING DIFFERENT AUTHENTICATION METHODS")
    print("=" * 60)
    
    # Method 1: Standard SSL with relaxed security
    print("\n1️⃣ Testing with relaxed SSL context...")
    try:
        # Create a more permissive SSL context
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        mail = imaplib.IMAP4_SSL("imap-mail.outlook.com", 993, ssl_context=context)
        result = mail.login(email, password)
        print(f"✅ Relaxed SSL - Login successful: {result}")
        mail.logout()
        return True
    except Exception as e:
        print(f"❌ Relaxed SSL failed: {e}")
    
    # Method 2: Try different port
    print("\n2️⃣ Testing with alternative port 143 + STARTTLS...")
    try:
        mail = imaplib.IMAP4("imap-mail.outlook.com", 143)
        mail.starttls()
        result = mail.login(email, password)
        print(f"✅ STARTTLS - Login successful: {result}")
        mail.logout()
        return True
    except Exception as e:
        print(f"❌ STARTTLS failed: {e}")
    
    # Method 3: Test account type detection
    print("\n3️⃣ Testing account type detection...")
    domain = email.split('@')[1].lower()
    print(f"Account domain: {domain}")
    
    if domain == "outlook.com":
        hosts_to_try = ["imap-mail.outlook.com", "imap.live.com"]
    elif domain == "hotmail.com":
        hosts_to_try = ["imap.live.com", "imap-mail.outlook.com"]
    else:
        hosts_to_try = ["outlook.office365.com", "imap-mail.outlook.com"]
    
    for host in hosts_to_try:
        print(f"  Trying {host}...")
        try:
            mail = imaplib.IMAP4_SSL(host, 993)
            result = mail.login(email, password)
            print(f"✅ {host} - Login successful: {result}")
            mail.logout()
            return True
        except Exception as e:
            print(f"❌ {host} failed: {e}")
    
    return False

def test_password_encoding():
    """Test if password encoding is an issue"""
    print("\n4️⃣ Testing password encoding...")
    
    # Try different encodings
    encodings_to_try = ['utf-8', 'ascii', 'latin-1']
    
    for encoding in encodings_to_try:
        try:
            encoded_password = password.encode(encoding).decode(encoding)
            print(f"  Testing with {encoding} encoding...")
            
            mail = imaplib.IMAP4_SSL("imap-mail.outlook.com", 993)
            result = mail.login(email, encoded_password)
            print(f"✅ {encoding} encoding - Login successful: {result}")
            mail.logout()
            return True
        except Exception as e:
            print(f"❌ {encoding} encoding failed: {e}")
    
    return False

def check_account_info():
    """Display account information for debugging"""
    print("\n🔍 ACCOUNT INFORMATION:")
    print(f"Email: {email}")
    print(f"Password length: {len(password)} characters")
    print(f"Password starts with: {password[:4]}...")
    print(f"Password ends with: ...{password[-4:]}")
    print(f"Domain: {email.split('@')[1] if '@' in email else 'Unknown'}")

if __name__ == "__main__":
    check_account_info()
    
    success = test_with_different_auth_methods()
    
    if not success:
        success = test_password_encoding()
    
    if success:
        print("\n🎉 AUTHENTICATION SUCCESSFUL!")
        print("Update your configuration with the working method.")
    else:
        print("\n❌ ALL AUTHENTICATION METHODS FAILED")
        print("\n💡 This suggests:")
        print("1. App password is incorrect or expired")
        print("2. Two-factor authentication is not properly configured")
        print("3. IMAP access is disabled for this account")
        print("4. Account requires OAuth2 (not supported in this test)")
        print("\nPlease:")
        print("- Generate a fresh app password")
        print("- Verify IMAP is enabled in Outlook settings")
        print("- Ensure two-factor authentication is active")