import pytest
from services.email_service import start_email_monitor, stop_email_monitor, send_test_email, send_email, send_daily_email

class DummyConfig:
    email_address = "test@example.com"
    email_password = "password"
    smtp_host = "smtp.test.com"
    smtp_port = 587
    smtp_use_tls = True
    timezone = "UTC"

def test_start_stop_email_monitor():
    # Should not raise
    start_email_monitor()
    stop_email_monitor()

def test_send_test_email():
    config = DummyConfig()
    send_test_email(config, "user@example.com")

def test_send_email():
    config = DummyConfig()
    send_email(config, "user@example.com", "Subject", "Body")

def test_send_daily_email():
    config = DummyConfig()
    user = {
        'email': "user@example.com",
        'weather_enabled': False,
        'countdown_enabled': False
    }
    send_daily_email(config, user)
