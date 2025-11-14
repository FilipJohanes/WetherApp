import imaplib
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

email = os.getenv("EMAIL_ADDRESS")
password = os.getenv("EMAIL_PASSWORD")
imap_host = os.getenv("IMAP_HOST")
imap_port = int(os.getenv("IMAP_PORT", "993"))

print(f"Testing IMAP connection to {imap_host}:{imap_port}")
print(f"Email: {email}")
print(f"Password: {password[:4]}...{password[-4:]} (showing first/last 4 chars)")

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
        if b'+ idling' in response.lower() or b'+ waiting' in response.lower():
            print("✅ IMAP IDLE supported!")
            mail.send(b'DONE\r\n')
            mail.readline()
        else:
            print(f"⚠️ IDLE response: {response}")
    except Exception as e:
        print(f"⚠️ IDLE test failed: {e}")
    
    mail.logout()
    print("✅ Test completed successfully!")
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\nTroubleshooting suggestions:")
    print("1. Double-check your app password is correct")
    print("2. Make sure 2FA is enabled on your Outlook account")
    print("3. Try generating a new app password")
    print("4. Check if there are any security notifications in Outlook")