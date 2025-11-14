"""
Alternative: Discord Bot Integration  
No phone number required - just create application on Discord Developer Portal
"""

import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Discord Bot Configuration
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_APPLICATION_ID = os.getenv('DISCORD_APPLICATION_ID')

def send_discord_message(channel_id, content):
    """Send message via Discord API"""
    try:
        headers = {
            'Authorization': f'Bot {DISCORD_BOT_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'content': content
        }
        
        url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code in [200, 204]:
            print(f"✅ Discord message sent to channel {channel_id}")
            return True
        else:
            print(f"❌ Discord API error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending Discord message: {e}")
        return False

@app.route('/webhook/discord', methods=['POST'])
def discord_webhook():
    """Handle Discord interactions"""
    try:
        data = request.get_json()
        
        # Handle slash commands
        if data.get('type') == 2:  # APPLICATION_COMMAND
            command_name = data.get('data', {}).get('name')
            channel_id = data.get('channel_id')
            
            if command_name == 'weather':
                weather_response = get_weather_response()
                
                # Respond to interaction
                return jsonify({
                    'type': 4,  # CHANNEL_MESSAGE_WITH_SOURCE
                    'data': {
                        'content': weather_response
                    }
                })
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        print(f"❌ Discord webhook error: {e}")
        return jsonify({'status': 'error'})

def get_weather_response():
    """Generate weather response"""
    return """🌤️ **Daily Weather Brief**
📍 Location: Your City
🌡️ Temperature: 15°C  
☁️ Conditions: Partly Cloudy
💨 Wind: 10 km/h

*Delivered with Pi Zero W2 efficiency!* ⚡"""

if __name__ == '__main__':
    print("🎮 Discord Bot Service Starting...")
    print(f"🤖 Bot Token: {DISCORD_BOT_TOKEN[:10]}..." if DISCORD_BOT_TOKEN else "❌ No token configured")
    app.run(host='0.0.0.0', port=5002, debug=False)