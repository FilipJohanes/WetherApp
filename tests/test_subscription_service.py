
import pytest
import sqlite3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app import init_db
from services.subscription_service import add_or_update_subscriber, delete_subscriber, get_subscriber


def test_add_and_get_subscriber(tmp_path):
    db_path = tmp_path / "test_subs.db"
    init_db(str(db_path))
    email = "user@example.com"
    add_or_update_subscriber(email, "Bratislava", 48.1, 17.1, "neutral", "en", "Europe/Bratislava", str(db_path))
    result = get_subscriber(email, str(db_path))
    assert result is not None
    assert result[0] == "Bratislava"


def test_update_subscriber(tmp_path):
    db_path = tmp_path / "test_subs.db"
    init_db(str(db_path))
    email = "user2@example.com"
    add_or_update_subscriber(email, "Bratislava", 48.1, 17.1, "neutral", "en", "Europe/Bratislava", str(db_path))
    add_or_update_subscriber(email, "Prague", 50.1, 14.4, "cute", "sk", "Europe/Prague", str(db_path))
    result = get_subscriber(email, str(db_path))
    assert result[0] == "Prague"
    assert result[3] == "cute"


def test_delete_subscriber(tmp_path):
    db_path = tmp_path / "test_subs.db"
    init_db(str(db_path))
    email = "user3@example.com"
    add_or_update_subscriber(email, "Bratislava", 48.1, 17.1, "neutral", "en", "Europe/Bratislava", str(db_path))
    count = delete_subscriber(email, str(db_path))
    assert count == 1
    result = get_subscriber(email, str(db_path))
    assert result is None
