import os
from typing import Dict, Optional
from services.summary_service import generate_weather_summary


import requests
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo
from services.subscription_service import get_subscriber
from services.email_service import send_daily_email
from services.logging_service import logger

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
	"""List all weather subscribers in the database."""
	conn = sqlite3.connect(db_path)
	try:
		cursor = conn.execute("SELECT email, location, lat, lon, personality, language, timezone FROM subscribers")
		subscribers = cursor.fetchall()
		if not subscribers:
			print("No subscribers found.")
			return
		print("Weather Subscribers:")
		for sub in subscribers:
			print(f"- {sub[0]} | {sub[1]} | {sub[2]}, {sub[3]} | {sub[4]} | {sub[5]} | {sub[6]}")
	finally:
		conn.close()

def run_daily_weather_job(config, dry_run=False, db_path="app.db"):
	"""Send daily weather emails to all subscribers."""
	logger.info("Running weather job - sending emails every 5 minutes for testing")
	conn = sqlite3.connect(db_path)
	try:
		subscribers = conn.execute("""
			SELECT email, location, lat, lon, COALESCE(timezone, 'UTC') as timezone,
				   COALESCE(personality, 'neutral') as personality, 
				   COALESCE(language, 'en') as language
			FROM subscribers 
			WHERE lat IS NOT NULL AND lon IS NOT NULL
		""").fetchall()
		logger.info(f"Checking {len(subscribers)} subscribers for test delivery")
		sent_count = 0
		for email_addr, location, lat, lon, subscriber_tz, personality, language in subscribers:
			try:
				subscriber_now = datetime.now(ZoneInfo(subscriber_tz))
				weather = get_weather_forecast(lat, lon, subscriber_tz)
				if not weather:
					logger.warning(f"No weather data for {email_addr} at {location}")
					continue
				# Use advanced summary generator for email body
				summary = generate_weather_summary(weather, location, personality, language)
				subject = f"Today's Weather for {location}"
				footer = f"\n\n---\nDaily Weather Service ({personality} mode, {language})\nTo unsubscribe, reply with 'delete'"
				full_message = summary + footer
				if dry_run:
					print(f"[DRY RUN] Would send test weather email to {email_addr} ({location}) at {subscriber_now.strftime('%H:%M')} {subscriber_tz} with weather: {weather}")
				else:
					send_daily_email(config, {
						'email': email_addr,
						'location': location,
						'lat': lat,
						'lon': lon,
						'personality': personality,
						'language': language,
						'timezone': subscriber_tz,
						'weather_enabled': True,
						'weather_data': weather,
						'email_body': full_message,
					})
					sent_count += 1
					logger.info(f"✅ Sent test weather to {email_addr} ({sent_count} total)")
			except Exception as e:
				logger.error(f"Error processing subscriber {email_addr}: {e}")
		if sent_count > 0:
			logger.info(f"✅ Test weather job complete - sent {sent_count} emails")
		else:
			logger.info("No emails sent this run")
	finally:
		conn.close()

