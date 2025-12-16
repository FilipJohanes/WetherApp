import os
from functools import lru_cache
import requests
import sqlite3
# from services.summary_service import generate_weather_summary  # merged below

def generate_weather_summary(weather, location, personality, language):


	if not weather:
		return f"Weather for {location} is unavailable."

	temp_max = weather.get('temp_max', 20)
	temp_min = weather.get('temp_min', 10)
	precipitation = weather.get('precipitation_sum', 0)
	wind_speed = weather.get('wind_speed_max', 5)
	rain_prob = min(int((precipitation / 1.5) * 100), 100) if precipitation else 0

	# Load weather_messages.txt (cache for performance)
	@lru_cache(maxsize=8)
	def load_weather_messages(lang):
		path = os.path.join(os.path.dirname(__file__), f'../languages/{lang}/weather_messages.txt')
		messages = {}
		if not os.path.exists(path):
			return messages
		with open(path, encoding='utf-8') as f:
			for line in f:
				line = line.strip()
				if not line or line.startswith('#'):
					continue
				parts = line.split('|')
				if len(parts) < 2:
					continue
				key = parts[0]
				personalities = ['neutral', 'cute', 'brutal', 'emuska']
				msg_map = dict(zip(personalities, parts[1:]))
				messages[key] = msg_map
		return messages

	messages = load_weather_messages(language)
	def get_msg(key, personality):
		msg_map = messages.get(key, {})
		return msg_map.get(personality) or msg_map.get('neutral') or messages.get('default', {}).get(personality, '')

	# Compose message
	intro = f"Today's weather for {location}:"
	temp_line = f"🌡️ Temperature: High {temp_max}°C / Low {temp_min}°C"
	rain_line = f"🌧️ Rain probability: {rain_prob}% (≈{precipitation} mm)"
	wind_line = f"💨 Wind: up to {wind_speed} km/h"

	# Determine weather condition using only keys from weather_messages.txt
	def get_condition(temp_max, temp_min, precipitation, wind_speed, rain_prob):
		# Combined conditions
		if temp_max >= 30 and rain_prob < 20:
			return 'sunny_hot'
		if temp_max <= 5 and wind_speed >= 15:
			return 'cold_windy'
		if temp_max <= 5 and precipitation >= 2:
			return 'rainy_cold'
		# Extreme conditions
		if temp_max >= 36:
			return 'heatwave'
		if temp_min <= -15:
			return 'blizzard'
		# Thunderstorm
		if precipitation >= 10 and rain_prob >= 70:
			return 'thunderstorm'
		# Heavy rain
		if precipitation >= 7:
			return 'heavy_rain'
		# Raining
		if precipitation >= 2:
			return 'raining'
		# Snowing
		if temp_max <= 2 and precipitation > 0.5:
			return 'snowing'
		# Freezing
		if temp_min < 0 and precipitation <= 0.1:
			return 'freezing'
		# Hot
		if temp_max >= 30:
			return 'hot'
		# Cold
		if temp_max <= 5:
			return 'cold'
		# Windy
		if wind_speed >= 15:
			return 'windy'
		# Foggy
		if temp_min >= -2 and temp_max <= 8 and precipitation < 0.2 and wind_speed < 8 and rain_prob >= 60:
			return 'foggy'
		# Humid
		if rain_prob >= 70 and precipitation < 0.2:
			return 'humid'
		# Dry
		if precipitation < 0.05 and temp_max >= 25:
			return 'dry'
		# Sunny
		if temp_max >= 20 and rain_prob < 20 and precipitation < 0.1:
			return 'sunny'
		# Mild
		if temp_max >= 10 and rain_prob < 40 and precipitation < 0.2:
			return 'mild'
		# Cloudy
		if rain_prob >= 30 or precipitation > 0.05:
			return 'cloudy'
		# Fallback
		return 'default'

	condition = get_condition(temp_max, temp_min, precipitation, wind_speed, rain_prob)
	condition_msg = get_msg(condition, personality)

	# Clothing suggestion logic: combine all relevant conditions
	clothing = set()
	# Add advice for temperature extremes
	if temp_max >= 36:
		clothing.add(get_msg('heatwave', personality).strip())
	if temp_min <= -15:
		clothing.add(get_msg('blizzard', personality).strip())
	if temp_max >= 30 and rain_prob < 20:
		clothing.add(get_msg('sunny_hot', personality).strip())
	if temp_max <= 5 and wind_speed >= 15:
		clothing.add(get_msg('cold_windy', personality).strip())
	if temp_max <= 5 and precipitation >= 2:
		clothing.add(get_msg('rainy_cold', personality).strip())
	# Add advice for rain and wind
	if precipitation >= 7:
		clothing.add(get_msg('heavy_rain', personality).strip())
	elif precipitation >= 2:
		clothing.add(get_msg('raining', personality).strip())
	if wind_speed >= 15:
		clothing.add(get_msg('windy', personality).strip())
	# Add advice for snow/freezing
	if temp_max <= 2 and precipitation > 0.5:
		clothing.add(get_msg('snowing', personality).strip())
	if temp_min < 0 and precipitation <= 0.1:
		clothing.add(get_msg('freezing', personality).strip())
	# Add advice for fog/humid/dry
	if temp_min >= -2 and temp_max <= 8 and precipitation < 0.2 and wind_speed < 8 and rain_prob >= 60:
		clothing.add(get_msg('foggy', personality).strip())
	if rain_prob >= 70 and precipitation < 0.2:
		clothing.add(get_msg('humid', personality).strip())
	if precipitation < 0.05 and temp_max >= 25:
		clothing.add(get_msg('dry', personality).strip())
	# Add advice for mild if nothing else
	if not clothing:
		clothing.add(get_msg('mild', personality).strip())
	# Remove empty, sort, and join
	clothing_msg = '\n'.join(sorted([c for c in clothing if c]))

	summary = f"{intro}\n\n{temp_line}\n{rain_line}\n{wind_line}\n\n{condition_msg}\n{clothing_msg}\n"
	return summary

def generate_countdown_summary(countdowns, language='en'):
	if not countdowns:
		return "No active countdowns."
	summary = "⏳ Countdown reminders:\n"
	for cd in countdowns:
		name = cd.get('name', 'Event')
		days = cd.get('days_left', '?')
		summary += f"• {name}: {days} days left\n"
	return summary

def generate_reminder_summary(reminders, language='en'):
	if not reminders:
		return "No active reminders."
	summary = "🔔 Reminders:\n"
	for r in reminders:
		text = r.get('text', 'Reminder')
		time = r.get('time', '')
		summary += f"• {text} {time}\n"
	return summary

def generate_daily_summary(weather=None, location=None, personality='neutral', language='en', countdowns=None, reminders=None):
	sections = []
	if weather and location:
		sections.append(generate_weather_summary(weather, location, personality, language))
	if countdowns:
		sections.append(generate_countdown_summary(countdowns, language))
	if reminders:
		sections.append(generate_reminder_summary(reminders, language))
	if not sections:
		return "No active subscriptions."
	return "\n\n".join(sections)
# --- END MERGED SUMMARY SERVICE ---



def get_weather_forecast(lat, lon, timezone):
	"""
	Fetch daily weather forecast for the given location using Open-Meteo API.
	Returns dict with temp_max, temp_min, precipitation_sum, wind_speed_max for today.
	"""
	url = "https://api.open-meteo.com/v1/forecast"
	params = {
		"latitude": lat,
		"longitude": lon,
		"daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max",
		"timezone": timezone,
	}
	try:
		response = requests.get(url, params=params, timeout=10)
		response.raise_for_status()
		data = response.json()
		daily = data.get("daily", {})
		# Get today's index (assume first in list)
		temp_max = daily.get("temperature_2m_max", [None])[0]
		temp_min = daily.get("temperature_2m_min", [None])[0]
		precipitation_sum = daily.get("precipitation_sum", [None])[0]
		wind_speed_max = daily.get("windspeed_10m_max", [None])[0]
		return {
			"temp_max": temp_max,
			"temp_min": temp_min,
			"precipitation_sum": precipitation_sum,
			"wind_speed_max": wind_speed_max,
		}
	except Exception as e:
		print(f"Weather API error for ({lat}, {lon}, {timezone}): {e}")
		return None

def geocode_location(location: str):
	"""
	Geocode a location string to (lat, lon, display_name, timezone_str) using Open-Meteo API.
	Returns (lat, lon, display_name, timezone_str) or None if not found.
	"""
	url = "https://geocoding-api.open-meteo.com/v1/search"
	params = {
		'name': location,
		'count': 1,
		'language': 'en',
		'format': 'json'
	}
	try:
		response = requests.get(url, params=params, timeout=10)
		response.raise_for_status()
		data = response.json()
		if data.get('results'):
			result = data['results'][0]
			lat = result['latitude']
			lon = result['longitude']
			name = result['name']
			country = result.get('country', '')
			admin1 = result.get('admin1', '')
			display_name = f"{name}"
			if admin1:
				display_name += f", {admin1}"
			if country:
				display_name += f", {country}"
			timezone_str = result.get('timezone', 'UTC')
			return lat, lon, display_name, timezone_str
		else:
			return None
	except Exception as e:
		print(f"Geocoding error for '{location}': {e}")
		return None

# weather_service.py
"""
Weather Service Module
Handles daily weather job and subscriber listing for the weather app.
"""

def list_subscribers(db_path="app.db"):
	"""List all weather subscribers from unified database."""
	conn = sqlite3.connect(db_path)
	conn.row_factory = sqlite3.Row
	try:
		cursor = conn.execute("""
			SELECT u.email, ws.location, u.lat, u.lon, ws.personality, ws.language, u.timezone
			FROM users u
			JOIN weather_subscriptions ws ON u.email = ws.email
			WHERE u.weather_enabled = 1
		""")
		subscribers = cursor.fetchall()
		if not subscribers:
			print("No weather subscribers found.")
			return
		print("Weather Subscribers:")
		for sub in subscribers:
			print(f"- {sub['email']} | {sub['location']} | {sub['lat']}, {sub['lon']} | {sub['personality']} | {sub['language']} | {sub['timezone']}")
	finally:
		conn.close()



