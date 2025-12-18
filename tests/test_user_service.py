import pytest
import sqlite3
import os
from services import user_service

def setup_module(module):
    # Use a test DB
    user_service.DB_PATH = 'test_app.db'
    conn = sqlite3.connect('test_app.db')
    conn.execute("DROP TABLE IF EXISTS users")
    conn.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            mfa_secret TEXT,
            status TEXT DEFAULT 'active',
            reset_token TEXT,
            reset_token_expiry TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def teardown_module(module):
    os.remove('test_app.db')

def test_register_and_authenticate():
    email = 'test@example.com'
    password = 'securepassword123'
    assert user_service.register_user(email, password)
    user_id = user_service.authenticate_user(email, password)
    assert user_id is not None
    # Wrong password
    assert user_service.authenticate_user(email, 'wrongpass') is None

def test_duplicate_registration():
    email = 'dup@example.com'
    password = 'password1'
    assert user_service.register_user(email, password)
    # Duplicate
    assert not user_service.register_user(email, 'password2')

def test_password_reset():
    email = 'reset@example.com'
    password = 'oldpass'
    new_password = 'newpass123'
    assert user_service.register_user(email, password)
    token = user_service.create_password_reset(email)
    assert token is not None
    # Reset with valid token
    assert user_service.reset_password(token, new_password)
    # Old password should fail
    assert user_service.authenticate_user(email, password) is None
    # New password should work
    assert user_service.authenticate_user(email, new_password) is not None

def test_user_status():
    email = 'status@example.com'
    password = 'pass'
    assert user_service.register_user(email, password)
    user = user_service.get_user_by_email(email)
    user_service.set_user_status(user[0], 'suspended')
    # Should not authenticate
    assert user_service.authenticate_user(email, password) is None
    user_service.set_user_status(user[0], 'active')
    # Should authenticate again
    assert user_service.authenticate_user(email, password) is not None
