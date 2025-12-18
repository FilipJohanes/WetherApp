import pytest
import threading
import pytest
import logging
import sys
from app import SafeStreamHandler, Config, load_env, init_db, main
 
def test_config_env(monkeypatch):
    monkeypatch.setenv("EMAIL_ADDRESS", "test@example.com")
    monkeypatch.setenv("EMAIL_PASSWORD", "password")
    monkeypatch.setenv("IMAP_HOST", "imap.test.com")
    monkeypatch.setenv("SMTP_HOST", "smtp.test.com")
    config = Config()
    assert config.email_address == "test@example.com"
    assert config.smtp_host == "smtp.test.com"


def test_load_env(monkeypatch):
    monkeypatch.setenv("EMAIL_ADDRESS", "test@example.com")
    monkeypatch.setenv("EMAIL_PASSWORD", "password")
    monkeypatch.setenv("IMAP_HOST", "imap.test.com")
    monkeypatch.setenv("SMTP_HOST", "smtp.test.com")
    config = load_env()
    assert config.email_address == "test@example.com"

def test_init_db(tmp_path):
    db_path = tmp_path / "test_app.db"
    init_db(str(db_path))
    assert db_path.exists()

def test_safe_stream_handler_unicode():
    handler = SafeStreamHandler(sys.stderr)
    record = logging.LogRecord("test", logging.INFO, "", 0, "emoji: 😃", None, None)
    # Should not raise
    handler.emit(record)

import pytest

@pytest.mark.skip(reason="main() starts blocking scheduler; skip in unit tests.")
def test_main_runs(monkeypatch):
    monkeypatch.setenv("EMAIL_ADDRESS", "test@example.com")
    monkeypatch.setenv("EMAIL_PASSWORD", "password")
    monkeypatch.setenv("IMAP_HOST", "imap.test.com")
    monkeypatch.setenv("SMTP_HOST", "smtp.test.com")
    # Should not raise (will exit early due to missing services)
    try:
        main()
    except SystemExit:
        pass


# Add more tests for threading, error states, and CLI as needed
