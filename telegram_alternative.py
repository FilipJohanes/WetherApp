"""
Alternative: Telegram Bot Integration
No phone number required - just create a bot with @BotFather
"""

import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')  # Get from @BotFather
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

def send_telegram_message(chat_id, text, parse_mode='Markdown'):
    """Send message via Telegram Bot API"""
    try:
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode
        }
        
        response = requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)
        
        if response.status_code == 200:
            print(f"✅ Telegram message sent to {chat_id}")
            return True
        else:
            print(f"❌ Telegram API error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending Telegram message: {e}")
        return False

@app.route('/webhook/telegram', methods=['POST'])
def telegram_webhook():
    """Handle incoming Telegram messages"""
    try:
        data = request.get_json()
        
        # Extract message info
        message = data.get('message', {})
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '').strip().lower()
        
        if not chat_id:
            return jsonify({'status': 'error', 'message': 'No chat_id found'})
        
        # Process weather request
        if 'weather' in text or 'počasie' in text:
            weather_response = get_weather_response()  # Your existing weather function
            send_telegram_message(chat_id, weather_response)
            
        elif 'start' in text:
            welcome_msg = """
🌤️ *Daily Brief Service*

Send me "weather" for current conditions
Send me "počasie" for Slovak weather

*Ultra-low resource usage for Pi Zero W2!*
            """
            send_telegram_message(chat_id, welcome_msg)
            
        return jsonify({'status': 'success'})
        
    except Exception as e:
        print(f"❌ Telegram webhook error: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

def get_weather_response():
    """Generate weather response (use your existing logic)"""
    return "🌤️ Today: 15°C, partly cloudy\n⏰ Generated at optimal Pi Zero efficiency!"

if __name__ == '__main__':
    print("📱 Telegram Bot Service Starting...")
    print(f"🤖 Bot Token: {TELEGRAM_BOT_TOKEN[:10]}..." if TELEGRAM_BOT_TOKEN else "❌ No token configured")
    app.run(host='0.0.0.0', port=5001, debug=False)