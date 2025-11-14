#!/usr/bin/env python3
"""
Quick test script to diagnose Outlook IMAP login issues
"""
import imaplib
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

email = os.getenv("EMAIL_ADDRESS")
password = os.getenv("EMAIL_PASSWORD")
imap_host = os.getenv("IMAP_HOST")
imap_port = int(os.getenv("IMAP_PORT", "993"))

print(f"🔐 Testing IMAP login...")
print(f"Email: {email}")
print(f"Password: {password}")
print(f"IMAP Host: {imap_host}")
print(f"IMAP Port: {imap_port}")
print("-" * 50)

def test_imap_connection():
    """Test IMAP connection with detailed error reporting"""
    try:
        print("1️⃣ Connecting to IMAP server...")
        mail = imaplib.IMAP4_SSL(imap_host, imap_port)
        print("✅ SSL connection established")
        
        print("2️⃣ Attempting login...")
        result = mail.login(email, password)
        print(f"✅ Login successful: {result}")
        
        print("3️⃣ Selecting INBOX...")
        mail.select('INBOX')
        print("✅ INBOX selected")
        
        print("4️⃣ Checking for messages...")
        typ, data = mail.search(None, 'ALL')
        message_count = len(data[0].split()) if data[0] else 0
        print(f"✅ Found {message_count} total messages")
        
        mail.close()
        mail.logout()
        print("✅ Connection closed successfully")
        
    except imaplib.IMAP4.error as e:
        print(f"❌ IMAP Error: {e}")
        return False
    except Exception as e:
        print(f"❌ General Error: {e}")
        return False
    
    return True

def test_alternative_hosts():
    """Test alternative IMAP hosts for Outlook"""
    alternative_hosts = [
        "imap-mail.outlook.com",
        "outlook.office365.com", 
        "imap.live.com",
        "imap.hotmail.com"
    ]
    
    print("\n🔍 Testing alternative IMAP hosts:")
    print("-" * 50)
    
    for host in alternative_hosts:
        print(f"\nTesting: {host}")
        try:
            mail = imaplib.IMAP4_SSL(host, 993)
            result = mail.login(email, password)
            print(f"✅ {host} - Login successful: {result}")
            mail.logout()
            return host
        except Exception as e:
            print(f"❌ {host} - Failed: {e}")
    
    return None

if __name__ == "__main__":
    print("🧪 OUTLOOK IMAP LOGIN DIAGNOSTIC TEST")
    print("=" * 50)
    
    if not all([email, password, imap_host]):
        print("❌ Missing required environment variables")
        print(f"EMAIL_ADDRESS: {'✅' if email else '❌'}")
        print(f"EMAIL_PASSWORD: {'✅' if password else '❌'}")  
        print(f"IMAP_HOST: {'✅' if imap_host else '❌'}")
        exit(1)
    
    # Test current configuration
    print("Testing current configuration:")
    success = test_imap_connection()
    
    if not success:
        print("\n" + "="*50)
        working_host = test_alternative_hosts()
        if working_host:
            print(f"\n🎉 Found working host: {working_host}")
            print("Update your .env file with this host!")
        else:
            print("\n💡 Suggestions:")
            print("1. Verify Outlook app password is correct")
            print("2. Enable two-factor authentication on Outlook account")
            print("3. Generate a new app password")
            print("4. Check if IMAP is enabled in Outlook settings")