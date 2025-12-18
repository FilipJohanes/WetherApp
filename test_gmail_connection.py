#!/usr/bin/env python3
"""
Gmail Connection Test Script
Tests SMTP connection and optionally sends a test email.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gmail_connection():
    """Test Gmail SMTP connection and credentials."""
    
    # Get credentials from environment
    email_user = os.getenv('EMAIL_USER', 'dailywether.reminder@gmail.com')
    email_password = os.getenv('EMAIL_PASSWORD', '')
    
    print("=" * 60)
    print("Gmail Connection Test")
    print("=" * 60)
    print(f"\n📧 Email User: {email_user}")
    print(f"🔑 Password Length: {len(email_password)} characters")
    print(f"🔑 Password (masked): {email_password[:4]}...{email_password[-4:] if len(email_password) > 8 else '****'}")
    
    if not email_password:
        print("\n❌ ERROR: EMAIL_PASSWORD not found in .env file!")
        print("\nPlease add to .env file:")
        print("EMAIL_PASSWORD=your-16-character-app-password")
        return False
    
    if len(email_password) != 16:
        print(f"\n⚠️ WARNING: Gmail App Passwords are typically 16 characters")
        print(f"   Your password is {len(email_password)} characters")
    
    # Test connection
    print("\n" + "=" * 60)
    print("Testing SMTP Connection...")
    print("=" * 60)
    
    try:
        # Connect to Gmail SMTP server
        print("\n[1/4] Connecting to smtp.gmail.com:587...")
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
        print("✅ Connected to SMTP server")
        
        # Start TLS
        print("\n[2/4] Starting TLS encryption...")
        server.starttls()
        print("✅ TLS encryption enabled")
        
        # Login
        print("\n[3/4] Authenticating with credentials...")
        server.login(email_user, email_password)
        print("✅ Authentication successful!")
        
        # Ask if user wants to send test email
        print("\n[4/4] Ready to send test email")
        send_test = input("\nSend a test email to verify delivery? (y/n): ").strip().lower()
        
        if send_test == 'y':
            recipient = input("Enter recipient email address: ").strip()
            if recipient:
                print(f"\n📤 Sending test email to {recipient}...")
                
                msg = MIMEMultipart()
                msg['From'] = email_user
                msg['To'] = recipient
                msg['Subject'] = "Daily Brief Service - Test Email"
                
                body = """
Hello!

This is a test email from your Daily Brief Service.

If you received this email, your Gmail SMTP connection is working correctly! ✅

Configuration Details:
- SMTP Server: smtp.gmail.com:587
- Authentication: Successful
- TLS Encryption: Enabled

You can now use the Daily Brief Service to send weather forecasts and reminders.

---
Daily Brief Service
Automated Email Testing
                """
                
                msg.attach(MIMEText(body, 'plain'))
                
                server.send_message(msg)
                print(f"✅ Test email sent successfully to {recipient}!")
                print("\n📬 Check your inbox (and spam folder) for the test email.")
        
        server.quit()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nYour Gmail connection is working correctly.")
        print("The Daily Brief Service should be able to send emails.")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"\n❌ AUTHENTICATION FAILED!")
        print(f"Error: {e}")
        print("\n🔧 How to fix:")
        print("1. Go to: https://myaccount.google.com/apppasswords")
        print("2. Generate a new App Password for 'Mail'")
        print("3. Update EMAIL_PASSWORD in your .env file")
        print("4. Remove any spaces from the password")
        print("5. Make sure 2-Step Verification is enabled on your Google Account")
        return False
        
    except smtplib.SMTPConnectError as e:
        print(f"\n❌ CONNECTION FAILED!")
        print(f"Error: {e}")
        print("\n🔧 Possible causes:")
        print("- No internet connection")
        print("- Firewall blocking port 587")
        print("- Gmail SMTP is down (unlikely)")
        return False
        
    except TimeoutError:
        print(f"\n❌ CONNECTION TIMEOUT!")
        print("\n🔧 Possible causes:")
        print("- No internet connection")
        print("- Network/firewall blocking Gmail")
        print("- DNS resolution issues")
        return False
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR!")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        return False

if __name__ == "__main__":
    try:
        success = test_gmail_connection()
        
        if success:
            print("\n✅ You're all set! The application should work correctly.")
        else:
            print("\n❌ Please fix the issues above and run this test again.")
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
