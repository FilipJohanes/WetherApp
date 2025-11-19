# weather_service.py
"""
Weather Service Module
Handles daily weather job and subscriber listing for the weather app.
"""
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo
from services.subscription_service import get_subscriber
from services.email_service import send_daily_email

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
	conn = sqlite3.connect(db_path)
	try:
		cursor = conn.execute("SELECT email, location, lat, lon, personality, language, timezone FROM subscribers")
		subscribers = cursor.fetchall()
		if not subscribers:
			print("No subscribers to send daily weather.")
			return
		for sub in subscribers:
			user = {
				'email': sub[0],
				'location': sub[1],
				'lat': sub[2],
				'lon': sub[3],
				'personality': sub[4],
				'language': sub[5],
				'timezone': sub[6],
				'weather_enabled': True,
				# 'weather_data': fetch_weather(sub[1], sub[2], sub[3]), # TODO: implement real fetch
			}
			if dry_run:
				print(f"[DRY RUN] Would send daily weather email to {user['email']} ({user['location']})")
			else:
				send_daily_email(config, user)
	finally:
		conn.close()

