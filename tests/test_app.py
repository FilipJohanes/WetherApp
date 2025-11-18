import pytest
import threading
import email
import types
from app import (
    SafeStreamHandler, EmailMessageInfo, Config, load_env, init_db, imap_fetch_unseen, _extract_plain_text,
    mark_seen, start_email_monitor_thread, stop_email_monitor, send_email, geocode_location, get_weather_forecast,
    generate_weather_summary, _generate_clothing_advice, handle_weather_command, run_daily_weather_job,
    process_inbound_email, should_process_email, check_inbox_job, list_subscribers, send_test_email, create_readme_if_missing
)

class TestConfig:
    def test_config_env(monkeypatch):
        monkeypatch.setenv("EMAIL_ADDRESS", "test@example.com")
        monkeypatch.setenv("EMAIL_PASSWORD", "password")
        monkeypatch.setenv("IMAP_HOST", "imap.test.com")
        monkeypatch.setenv("SMTP_HOST", "smtp.test.com")
        config = Config()
        assert config.email_address == "test@example.com"
        assert config.smtp_host == "smtp.test.com"

class TestEmailMessageInfo:
    def test_namedtuple_fields(self):
        msg = EmailMessageInfo("uid1", "user@example.com", "Subject", "Body", types.SimpleNamespace())
        assert msg.uid == "uid1"
        assert msg.from_email == "user@example.com"

class TestExtractPlainText:
    def test_extract_plain_text_simple(self):
        msg = email.message_from_string("Content-Type: text/plain\n\nHello world!")
        assert _extract_plain_text(msg) == "Hello world!"

class TestSendEmail:
    def test_send_email_dry_run(self, config):
        result = send_email(config, "user@example.com", "Test", "Body", dry_run=True)
        assert result is True

class TestGeocodeLocation:
    def test_geocode_location_invalid(self):
        result = geocode_location("")
        assert result is None

class TestWeatherForecast:
    def test_weather_forecast_invalid(self):
        result = get_weather_forecast(0, 0, "Invalid/Zone")
        assert result is None

class TestGenerateWeatherSummary:
    def test_generate_weather_summary(self):
        weather = {'temp_max': 20, 'temp_min': 10, 'precipitation_probability': 10, 'precipitation_sum': 0, 'wind_speed_max': 5}
        summary = generate_weather_summary(weather, "Bratislava", "neutral", "en")
        assert "Bratislava" in summary
        assert "Temperature" in summary

class TestClothingAdvice:
    def test_clothing_advice(self):
        advice = _generate_clothing_advice(5, 60, 2, 35, "cute", "en")
        assert "jacket" in advice or "umbrella" in advice

class TestShouldProcessEmail:
    def test_should_process_email_system(self):
        msg = EmailMessageInfo("uid", "no-reply@google.com", "Subject", "Body", types.SimpleNamespace())
        assert not should_process_email(msg)

class TestCreateReadme:
    def test_create_readme(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        create_readme_if_missing()
        assert (tmp_path / "README.md").exists()

# Add more tests for threading, error states, and CLI as needed
