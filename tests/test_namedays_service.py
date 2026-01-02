"""
Tests for namedays_service.py
"""
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.namedays_service import load_nameday_data, get_nameday_message


def test_load_nameday_data_slovak():
	"""Test loading Slovak nameday data"""
	message_prefix, namedays_dict = load_nameday_data('sk')
	
	assert message_prefix is not None
	assert message_prefix == "Dnes má meniny:"
	assert namedays_dict is not None
	assert len(namedays_dict) > 0
	# Check specific date
	assert '01-02' in namedays_dict
	assert namedays_dict['01-02'] == 'Alexandra'


def test_load_nameday_data_czech():
	"""Test loading Czech nameday data"""
	message_prefix, namedays_dict = load_nameday_data('cz')
	
	assert message_prefix is not None
	assert message_prefix == "Dnes má svátek:"
	assert namedays_dict is not None
	assert '01-02' in namedays_dict
	assert namedays_dict['01-02'] == 'Karina'


def test_load_nameday_data_hungarian():
	"""Test loading Hungarian nameday data"""
	message_prefix, namedays_dict = load_nameday_data('hu')
	
	assert message_prefix is not None
	assert message_prefix == "Ma van névnapja:"
	assert namedays_dict is not None
	assert '01-02' in namedays_dict
	assert namedays_dict['01-02'] == 'Ábel'


def test_load_nameday_data_unsupported_language():
	"""Test loading nameday data for unsupported language"""
	message_prefix, namedays_dict = load_nameday_data('en')
	
	assert message_prefix is None
	assert namedays_dict is None


def test_get_nameday_message_with_name():
	"""Test getting nameday message for a date with names"""
	# January 2nd - Slovak
	test_date = datetime(2026, 1, 2)
	message = get_nameday_message('sk', test_date)
	
	assert message == "Dnes má meniny: Alexandra"


def test_get_nameday_message_with_multiple_names():
	"""Test getting nameday message for a date with multiple names"""
	# June 29th - Slovak (Pavol, Peter, Petra)
	test_date = datetime(2026, 6, 29)
	message = get_nameday_message('sk', test_date)
	
	assert "Dnes má meniny:" in message
	assert "Pavol" in message


def test_get_nameday_message_no_name():
	"""Test getting nameday message for a date without names"""
	# January 1st - Slovak (empty)
	test_date = datetime(2026, 1, 1)
	message = get_nameday_message('sk', test_date)
	
	assert message == ""


def test_get_nameday_message_unsupported_language():
	"""Test getting nameday message for unsupported language"""
	test_date = datetime(2026, 1, 2)
	message = get_nameday_message('en', test_date)
	
	assert message == ""


def test_get_nameday_message_current_date():
	"""Test getting nameday message for current date (no date parameter)"""
	# This will use today's date
	message_sk = get_nameday_message('sk')
	message_en = get_nameday_message('en')
	
	# Slovak should return something or empty (depending on today's date)
	assert isinstance(message_sk, str)
	# English should return empty (not supported)
	assert message_en == ""


def test_get_nameday_message_czech_specific():
	"""Test Czech nameday for specific date"""
	# January 2nd - Czech
	test_date = datetime(2026, 1, 2)
	message = get_nameday_message('cz', test_date)
	
	assert message == "Dnes má svátek: Karina"


def test_get_nameday_message_hungarian_specific():
	"""Test Hungarian nameday for specific date"""
	# January 2nd - Hungarian
	test_date = datetime(2026, 1, 2)
	message = get_nameday_message('hu', test_date)
	
	assert message == "Ma van névnapja: Ábel"


if __name__ == '__main__':
	print("Running namedays service tests...")
	test_load_nameday_data_slovak()
	print("✓ Slovak data loads correctly")
	
	test_load_nameday_data_czech()
	print("✓ Czech data loads correctly")
	
	test_load_nameday_data_hungarian()
	print("✓ Hungarian data loads correctly")
	
	test_load_nameday_data_unsupported_language()
	print("✓ Unsupported language returns None")
	
	test_get_nameday_message_with_name()
	print("✓ Message with name works")
	
	test_get_nameday_message_with_multiple_names()
	print("✓ Message with multiple names works")
	
	test_get_nameday_message_no_name()
	print("✓ Empty date returns empty string")
	
	test_get_nameday_message_unsupported_language()
	print("✓ Unsupported language message returns empty")
	
	test_get_nameday_message_current_date()
	print("✓ Current date message works")
	
	test_get_nameday_message_czech_specific()
	print("✓ Czech specific message works")
	
	test_get_nameday_message_hungarian_specific()
	print("✓ Hungarian specific message works")
	
	print("\nAll tests passed! ✓")
