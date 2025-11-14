#!/usr/bin/env python3
"""
Daily Brief Service - Deployment Manager
Easily switch between Email polling and WhatsApp webhook modes
Optimized for Raspberry Pi Zero W2
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_requirements():
    """Check if all requirements are installed"""
    try:
        import flask
        import requests
        print("✅ Flask and requests are installed")
        return True
    except ImportError:
        print("❌ Missing requirements. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "flask", "requests"])
        return True

def check_whatsapp_config():
    """Check if WhatsApp is configured"""
    required_vars = [
        "WHATSAPP_ACCESS_TOKEN",
        "WHATSAPP_PHONE_NUMBER_ID", 
        "WHATSAPP_WEBHOOK_VERIFY_TOKEN"
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Missing WhatsApp config: {', '.join(missing)}")
        print("📖 See WHATSAPP_SETUP_GUIDE.md for setup instructions")
        return False
    else:
        print("✅ WhatsApp configuration found")
        return True

def start_email_mode():
    """Start the traditional email polling service"""
    print("📧 Starting Email Polling Mode...")
    print("⚠️  Resource usage: ~1.8% CPU, 60 polls/hour")
    
    try:
        # Load environment
        from dotenv import load_dotenv
        load_dotenv()
        
        # Import and run the main app
        from app import main
        main()
        
    except KeyboardInterrupt:
        print("\n📧 Email service stopped")
    except Exception as e:
        print(f"❌ Email service error: {e}")

def start_telegram_mode():
    """Start the Telegram bot service"""
    print("🤖 Starting Telegram Bot Mode...")
    print("📱 No phone number required!")
    print("⚡ Resource usage: ~0.1% CPU, event-driven")
    
    try:
        from telegram_alternative import app
        port = int(os.getenv('PORT', 5001))
        host = os.getenv('HOST', '0.0.0.0')
        
        print(f"🚀 Telegram bot starting on {host}:{port}")
        print(f"🤖 Webhook: http://{host}:{port}/webhook/telegram")
        
        app.run(host=host, port=port, debug=False)
        
    except KeyboardInterrupt:
        print("\n🤖 Telegram service stopped")
    except Exception as e:
        print(f"❌ Telegram service error: {e}")

def start_discord_mode():
    """Start the Discord bot service"""
    print("🎮 Starting Discord Bot Mode...")
    print("📱 No phone number required!")
    print("⚡ Resource usage: ~0.1% CPU, event-driven")
    
    try:
        from discord_alternative import app
        port = int(os.getenv('PORT', 5002))
        host = os.getenv('HOST', '0.0.0.0')
        
        print(f"🚀 Discord bot starting on {host}:{port}")
        print(f"🎮 Webhook: http://{host}:{port}/webhook/discord")
        
        app.run(host=host, port=port, debug=False)
        
    except KeyboardInterrupt:
        print("\n🎮 Discord service stopped")
    except Exception as e:
        print(f"❌ Discord service error: {e}")

def start_web_mode():
    """Start the web dashboard service"""
    print("🌐 Starting Web Dashboard Mode...")
    print("📱 No external services required!")
    print("⚡ Resource usage: ~0.2% CPU, web interface")
    
    try:
        from web_dashboard import app
        port = int(os.getenv('PORT', 5003))
        host = os.getenv('HOST', '0.0.0.0')
        
        print(f"🚀 Web dashboard starting on {host}:{port}")
        print(f"🌐 Access: http://{host}:{port}")
        print(f"📊 Dashboard: http://localhost:{port}")
        
        app.run(host=host, port=port, debug=False)
        
    except KeyboardInterrupt:
        print("\n🌐 Web dashboard stopped")
    except Exception as e:
        print(f"❌ Web dashboard error: {e}")

def start_whatsapp_mode():
    """Start the WhatsApp webhook service"""
    if not check_whatsapp_config():
        print("🔧 Please configure WhatsApp first")
        return
    
    print("📱 Starting WhatsApp Webhook Mode...")
    print("⚡ Resource usage: ~0.1% CPU, event-driven")
    
    try:
        # Patch the email system for WhatsApp compatibility
        from whatsapp_adapter import patch_email_system
        patch_email_system()
        
        # Start WhatsApp service
        from whatsapp_service import app
        port = int(os.getenv('PORT', 5000))
        host = os.getenv('HOST', '0.0.0.0')
        
        print(f"🚀 WhatsApp service starting on {host}:{port}")
        print(f"📱 Webhook: http://{host}:{port}/webhook/whatsapp")
        
        app.run(host=host, port=port, debug=False)
        
    except KeyboardInterrupt:
        print("\n📱 WhatsApp service stopped")
    except Exception as e:
        print(f"❌ WhatsApp service error: {e}")

def start_hybrid_mode():
    """Start both email and WhatsApp services"""
    print("🔀 Starting Hybrid Mode (Email + WhatsApp)...")
    print("📧 Email polling for backup/legacy users")
    print("📱 WhatsApp for real-time users") 
    
    import threading
    import time
    
    # Start WhatsApp service in background thread
    if check_whatsapp_config():
        whatsapp_thread = threading.Thread(target=start_whatsapp_mode, daemon=True)
        whatsapp_thread.start()
        time.sleep(2)  # Let WhatsApp start first
    
    # Start email service in main thread
    start_email_mode()

def show_status():
    """Show current service status and configuration"""
    print("📊 Daily Brief Service Status")
    print("=" * 40)
    
    # Check email config
    email_configured = bool(os.getenv("EMAIL_ADDRESS") and os.getenv("EMAIL_PASSWORD"))
    print(f"📧 Email: {'✅ Configured' if email_configured else '❌ Not configured'}")
    
    # Check WhatsApp config  
    whatsapp_configured = check_whatsapp_config()
    print(f"📱 WhatsApp: {'✅ Configured' if whatsapp_configured else '❌ Not configured'}")
    
    # Show recommended mode
    if whatsapp_configured and email_configured:
        print("🎯 Recommended: --hybrid (best of both)")
    elif whatsapp_configured:
        print("🎯 Recommended: --whatsapp (optimal for Pi Zero)")  
    elif email_configured:
        print("🎯 Recommended: --email (traditional mode)")
    else:
        print("❌ No services configured")
    
    # Show resource usage
    print("\n📊 Resource Comparison:")
    print("📧 Email:    1.8% CPU, 60 polls/hour, 60s response")
    print("📱 WhatsApp: 0.1% CPU, event-driven, 1-5s response")

def setup_systemd_service(mode: str):
    """Generate systemd service file for automatic startup"""
    service_content = f"""[Unit]
Description=Daily Brief Service ({mode.title()})
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory={Path.cwd()}
Environment=PATH={Path.cwd()}/venv/bin
EnvironmentFile={Path.cwd()}/.env
ExecStart={sys.executable} {__file__} --{mode}
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
    
    service_file = f"daily-brief-{mode}.service"
    with open(service_file, 'w') as f:
        f.write(service_content)
    
    print(f"📄 Created {service_file}")
    print(f"📋 To install: sudo cp {service_file} /etc/systemd/system/")
    print(f"📋 To enable: sudo systemctl enable daily-brief-{mode}")
    print(f"📋 To start: sudo systemctl start daily-brief-{mode}")

def main():
    parser = argparse.ArgumentParser(description='Daily Brief Service Deployment Manager')
    parser.add_argument('--email', action='store_true', help='Start email polling mode')
    parser.add_argument('--whatsapp', action='store_true', help='Start WhatsApp webhook mode (requires phone number)')
    parser.add_argument('--telegram', action='store_true', help='Start Telegram bot mode (NO phone number required)')
    parser.add_argument('--discord', action='store_true', help='Start Discord bot mode (NO phone number required)')
    parser.add_argument('--web', action='store_true', help='Start web dashboard mode (NO external services required)')
    parser.add_argument('--hybrid', action='store_true', help='Start both email and WhatsApp')
    parser.add_argument('--status', action='store_true', help='Show configuration status')
    parser.add_argument('--systemd', choices=['email', 'whatsapp', 'telegram', 'discord', 'web', 'hybrid'], 
                       help='Generate systemd service file')
    parser.add_argument('--test', action='store_true', help='Test configuration')
    
    args = parser.parse_args()
    
    # Check requirements first
    if not check_requirements():
        return
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️ python-dotenv not installed, using system environment")
    
    if args.status:
        show_status()
    elif args.systemd:
        setup_systemd_service(args.systemd)
    elif args.test:
        print("🧪 Testing configuration...")
        show_status()
        # Add more tests here
    elif args.telegram:
        start_telegram_mode()
    elif args.discord:
        start_discord_mode()
    elif args.web:
        start_web_mode()
    elif args.email:
        start_email_mode()
    elif args.whatsapp:
        start_whatsapp_mode()
    elif args.hybrid:
        start_hybrid_mode()
    else:
        print("🚀 Daily Brief Service - Deployment Manager")
        print("=" * 45)
        print("Usage:")
        print("  python deploy.py --email      # Email polling mode")
        print("  python deploy.py --whatsapp   # WhatsApp webhook mode (requires phone number)") 
        print("  python deploy.py --telegram   # Telegram bot mode (NO phone required)")
        print("  python deploy.py --discord    # Discord bot mode (NO phone required)")
        print("  python deploy.py --web        # Web dashboard mode (NO external services)")
        print("  python deploy.py --hybrid     # Both email + WhatsApp")
        print("  python deploy.py --status     # Show configuration")
        print("  python deploy.py --systemd hybrid  # Generate service file")
        print("")
        print("📱 No Phone Number? Try:")
        print("   --telegram  (Create bot with @BotFather)")
        print("   --discord   (Discord Developer Portal)")  
        print("   --web       (Pure web interface)")
        print("")
        print("For Pi Zero W2, use --telegram or --web for optimal performance!")

if __name__ == "__main__":
    main()