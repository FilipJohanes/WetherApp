#!/usr/bin/env python3
"""
WhatsApp Message Adapter
Seamlessly integrates WhatsApp messages with existing Daily Brief Service logic.
Converts WhatsApp format to EmailMessageInfo for compatibility.
"""

from typing import Dict, Optional
from datetime import datetime
from app import EmailMessageInfo, send_email, Config

def send_whatsapp_response(config: Config, to_phone: str, subject: str, body: str, dry_run: bool = False) -> bool:
    """
    Send response via WhatsApp (adapts existing send_email function)
    Falls back to email if WhatsApp is not configured
    """
    # Extract phone number from whatsapp email format
    if "@whatsapp.com" in to_phone:
        phone_number = to_phone.split("@")[0]
        
        # Try WhatsApp first
        if has_whatsapp_config():
            try:
                from whatsapp_service import send_whatsapp_message
                
                # Format message for WhatsApp (remove email subject)
                whatsapp_message = f"{subject}\n\n{body}" if subject else body
                
                if dry_run:
                    print(f"DRY RUN - Would send WhatsApp to {phone_number}: {whatsapp_message[:100]}...")
                    return True
                    
                return send_whatsapp_message(f"+{phone_number}", whatsapp_message)
                
            except Exception as e:
                print(f"WhatsApp send failed, falling back to email: {e}")
        
        # Fallback: Convert phone to email format
        fallback_email = f"user+{phone_number}@gmail.com"  # User's actual email
        return send_email(config, fallback_email, subject, body, dry_run)
    else:
        # Regular email
        return send_email(config, to_phone, subject, body, dry_run)

def has_whatsapp_config() -> bool:
    """Check if WhatsApp is properly configured"""
    import os
    return bool(os.getenv("WHATSAPP_ACCESS_TOKEN") and os.getenv("WHATSAPP_PHONE_NUMBER_ID"))

def format_weather_for_whatsapp(weather_message: str) -> str:
    """
    Format weather message for WhatsApp with emojis and better structure
    """
    # Add WhatsApp-friendly formatting
    lines = weather_message.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Add emojis to key weather elements
        if 'Temperature' in line or 'Teplota' in line:
            line = f"🌡️ {line}"
        elif 'Rain' in line or 'Dážd' in line or 'precipitation' in line.lower():
            line = f"🌧️ {line}"  
        elif 'Wind' in line or 'Vietor' in line:
            line = f"💨 {line}"
        elif 'Humidity' in line or 'Vlhkost' in line:
            line = f"💧 {line}"
        elif 'Pressure' in line or 'Tlak' in line:
            line = f"📊 {line}"
        elif any(word in line.lower() for word in ['sunny', 'slnečno', 'clear']):
            line = f"☀️ {line}"
        elif any(word in line.lower() for word in ['cloudy', 'oblačno', 'cloud']):
            line = f"☁️ {line}"
        elif any(word in line.lower() for word in ['storm', 'búrka', 'thunder']):
            line = f"⛈️ {line}"
            
        formatted_lines.append(line)
    
    # Add footer for WhatsApp
    formatted_message = '\n'.join(formatted_lines)
    formatted_message += "\n\n💬 Reply 'help' for commands or 'delete' to unsubscribe"
    
    return formatted_message

def create_whatsapp_quick_replies(language: str = 'en') -> Dict:
    """Create quick reply buttons for WhatsApp"""
    if language == 'sk':
        return {
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": "Potrebujete pomoc s počasím?"},
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "help", "title": "📖 Pomoc"}},
                        {"type": "reply", "reply": {"id": "cute", "title": "💕 Roztomilé"}},
                        {"type": "reply", "reply": {"id": "brutal", "title": "😤 Drsné"}}
                    ]
                }
            }
        }
    elif language == 'es':
        return {
            "type": "interactive", 
            "interactive": {
                "type": "button",
                "body": {"text": "¿Necesitas ayuda con el clima?"},
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "help", "title": "📖 Ayuda"}},
                        {"type": "reply", "reply": {"id": "cute", "title": "💕 Lindo"}},
                        {"type": "reply", "reply": {"id": "brutal", "title": "😤 Brutal"}}
                    ]
                }
            }
        }
    else:  # English
        return {
            "type": "interactive",
            "interactive": {
                "type": "button", 
                "body": {"text": "Need help with weather?"},
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "help", "title": "📖 Help"}},
                        {"type": "reply", "reply": {"id": "cute", "title": "💕 Cute"}},
                        {"type": "reply", "reply": {"id": "brutal", "title": "😤 Brutal"}}
                    ]
                }
            }
        }

# Patch the existing send_email function to use WhatsApp when available
def patch_email_system():
    """
    Monkey patch the existing app to use WhatsApp when possible
    This allows seamless integration without changing existing code
    """
    import app
    
    # Store original send_email function
    app._original_send_email = app.send_email
    
    # Replace with WhatsApp-aware version
    def whatsapp_aware_send_email(config, to_email, subject, body, dry_run=False):
        if "@whatsapp.com" in to_email:
            return send_whatsapp_response(config, to_email, subject, body, dry_run)
        else:
            return app._original_send_email(config, to_email, subject, body, dry_run)
    
    app.send_email = whatsapp_aware_send_email
    print("✅ Email system patched for WhatsApp support")

if __name__ == "__main__":
    # Test the adapter
    print("🧪 Testing WhatsApp adapter...")
    
    # Test message formatting
    sample_weather = """Today's weather for Bratislava:
    
Temperature: High 18°C / Low 12°C  
Rain probability: 70% (≈3.0 mm)
Wind: 15 km/h from SW
Humidity: 82%

Take an umbrella - it's going to rain today."""

    formatted = format_weather_for_whatsapp(sample_weather)
    print("📱 WhatsApp formatted message:")
    print(formatted)
    
    print("\n✅ WhatsApp adapter ready!")