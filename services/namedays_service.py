"""
Name day service for loading and retrieving name day information.
Supports multiple languages with localized messages.
"""
import os
from datetime import datetime


def load_nameday_data(language='en'):
	"""
	Load nameday data from namedays.txt for the given language.
	Returns tuple: (message_prefix, namedays_dict) or (None, None) if not supported.
	"""
	file_path = os.path.join(os.path.dirname(__file__), '..', 'languages', language, 'namedays.txt')
	if not os.path.exists(file_path):
		return None, None
	
	message_prefix = None
	namedays_dict = {}
	
	try:
		with open(file_path, 'r', encoding='utf-8') as f:
			for line in f:
				line = line.strip()
				if not line:
					continue
				if line.startswith('# Message:'):
					message_prefix = line.replace('# Message:', '').strip()
					continue
				if line.startswith('#'):
					continue
				if '=' in line:
					date_key, names = line.split('=', 1)
					namedays_dict[date_key.strip()] = names.strip()
	except Exception as e:
		print(f"Warning: Could not load namedays for language {language}: {e}")
		return None, None
	
	return message_prefix, namedays_dict


def get_nameday_message(language='en', date=None):
	"""
	Get the nameday message for today (or specified date) in the given language.
	Returns formatted message string, or empty string if no nameday or not supported.
	"""
	message_prefix, namedays_dict = load_nameday_data(language)
	
	# If language doesn't support namedays, return empty
	if message_prefix is None or namedays_dict is None:
		return ""
	
	# Get date in MM-DD format
	if date is None:
		date = datetime.now()
	date_key = date.strftime('%m-%d')
	
	# Get names for this date
	names = namedays_dict.get(date_key, '')
	
	# If no names for today, return empty
	if not names:
		return ""
	
	# Return formatted message
	return f"{message_prefix} {names}"
