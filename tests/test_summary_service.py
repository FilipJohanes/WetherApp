import pytest
from services.summary_service import generate_weather_summary

def test_generate_weather_summary_basic():
    weather = {'temp_max': 25, 'temp_min': 15, 'precipitation_sum': 0, 'wind_speed_max': 10}
    summary = generate_weather_summary(weather, "Bratislava", "neutral", "en")
    assert "Bratislava" in summary
    assert "Temperature" in summary
    assert "Wind" in summary

def test_generate_weather_summary_missing_weather():
    summary = generate_weather_summary(None, "Bratislava", "neutral", "en")
    assert "unavailable" in summary
