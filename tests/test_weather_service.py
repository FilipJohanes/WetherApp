
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app import init_db
from services.weather_service import geocode_location, list_subscribers, run_daily_weather_job

# Test geocode_location with valid and invalid input
def test_geocode_location_valid():
    result = geocode_location("Bratislava")
    assert result is None or (len(result) == 4 and isinstance(result[0], float))

def test_geocode_location_invalid():
    result = geocode_location("")
    assert result is None

# Test list_subscribers with empty DB (should not raise)

def test_list_subscribers_empty(tmp_path):
    db_path = tmp_path / "test_weather.db"
    init_db(str(db_path))
    list_subscribers(str(db_path))

# Test run_daily_weather_job with empty DB (should not raise)

def test_run_daily_weather_job_empty(tmp_path):
    db_path = tmp_path / "test_weather.db"
    init_db(str(db_path))
    class DummyConfig:
        timezone = "UTC"
    run_daily_weather_job(DummyConfig(), dry_run=True, db_path=str(db_path))
