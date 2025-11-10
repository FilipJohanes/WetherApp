import imaplib
import os
from dotenv import load_dotenv

# Force load from .env file in current directory
load_dotenv('.env', override=True)

print("="*60)
print("ENVIRONMENT VARIABLES CHECK")
print("="*60)

# Check what's actually being loaded
print(f"Current working directory: {os.getcwd()}")
print(f"EMAIL_ADDRESS from env: {os.getenv('EMAIL_ADDRESS')}")
print(f"EMAIL_PASSWORD from env: {os.getenv('EMAIL_PASSWORD')}")
print(f"IMAP_HOST from env: {os.getenv('IMAP_HOST')}")
print(f"IMAP_PORT from env: {os.getenv('IMAP_PORT')}")

# Read .env file directly
print()
print("📄 Reading .env file directly:")
try:
    with open('.env', 'r') as f:
        for line_num, line in enumerate(f, 1):
            if line.strip() and not line.strip().startswith('#'):
                print(f"   Line {line_num}: {line.strip()}")
except FileNotFoundError:
    print("   ❌ .env file not found!")

print()
print("="*60)
print("TESTING OUTLOOK CONNECTION")
print("="*60)

# Use the values directly from .env
email = "daily.weather@outlook.com"
password = "ctbwyvmipghkwhyk"
imap_host = "outlook.office365.com"
imap_port = 993

print(f"Email: {email}")
print(f"Password: {password[:4]}...{password[-4:]}")
print(f"IMAP Host: {imap_host}:{imap_port}")
print()

try:
    # Test connection
    mail = imaplib.IMAP4_SSL(imap_host, imap_port)
    print("✅ Connected to IMAP server")
    
    # Test login
    response = mail.login(email, password)
    print(f"✅ Login successful: {response}")
    
    # Test selecting inbox
    mail.select('INBOX')
    print("✅ Inbox selected successfully")
    
    # Test IDLE support
    try:
        mail.send(b'IDLE\r\n')
        response = mail.readline()
        print(f"📧 IDLE response: {response}")
        if b'+ idling' in response.lower() or b'+ waiting' in response.lower():
            print("✅ IMAP IDLE supported!")
            mail.send(b'DONE\r\n')
            mail.readline()
        else:
            print("⚠️ IMAP IDLE not supported")
    except Exception as e:
        print(f"⚠️ IDLE test failed: {e}")
    
    mail.logout()
    print("✅ Test completed successfully!")
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    if "LOGIN failed" in str(e):
        print()
        print("🔧 LOGIN FAILED - Possible causes:")
        print("   1. App password is incorrect")
        print("   2. App password not activated yet (wait 5-10 minutes)")
        print("   3. 2FA not properly enabled")
        print("   4. Account has security restrictions")
        print("   5. Need to approve sign-in from new location")