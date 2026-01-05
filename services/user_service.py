
import sqlite3
import hashlib
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional
import bcrypt

"""
User Service Module
Handles registration, authentication, and user management for user accounts.
"""

def get_db_path():
    return os.getenv("APP_DB_PATH", "app.db")

# Password hashing helpers

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())

# User registration

def register_user(email: str, password: str, nickname: str = None, username: str = None, 
                  email_consent: bool = False, terms_accepted: bool = False) -> tuple[bool, str]:
    """Register a new user with email and password."""
    password_hash = hash_password(password)
    now = datetime.utcnow().isoformat()
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    try:
        # Check if user already exists
        existing = conn.execute("SELECT email FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            return False, "Email already registered"
        
        conn.execute("""
            INSERT INTO users (email, username, nickname, password_hash, 
                             email_consent, terms_accepted, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (email, username, nickname, password_hash, 
              1 if email_consent else 0, 1 if terms_accepted else 0, now, now))
        conn.commit()
        return True, "Registration successful"
    except sqlite3.IntegrityError as e:
        return False, f"Database error: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"
    finally:
        conn.close()

# User authentication

def authenticate_user(email: str, password: str) -> Optional[dict]:
    """Authenticate user and return user data if successful."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute("""
            SELECT email, username, nickname, password_hash 
            FROM users WHERE email = ?
        """, (email,)).fetchone()
        if not row:
            return None
        
        password_hash = row['password_hash']
        if not password_hash:
            return None  # No password set
        
        if verify_password(password, password_hash):
            return {
                'email': row['email'],
                'username': row['username'],
                'nickname': row['nickname']
            }
        return None
    finally:
        conn.close()

def get_user_by_email(email: str) -> Optional[dict]:
    """Get user data by email."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute("""
            SELECT email, username, nickname, timezone, subscription_type,
                   weather_enabled, countdown_enabled, reminder_enabled,
                   created_at, updated_at
            FROM users WHERE email = ?
        """, (email,)).fetchone()
        if row:
            return dict(row)
        return None
    finally:
        conn.close()

# Note: Password reset functionality is handled via the password_reset_tokens table in api.py
# The old create_password_reset and reset_password functions that used users table columns
# have been removed as they referenced non-existent columns (reset_token, reset_token_expiry).
# Use the API endpoints /api/users/password-reset-request and /api/users/password-reset instead.

def get_user_by_email(email: str) -> Optional[dict]:
    """Get user data by email."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute("""
            SELECT email, username, nickname, timezone, subscription_type,
                   weather_enabled, countdown_enabled, reminder_enabled,
                   created_at, updated_at
            FROM users WHERE email = ?
        """, (email,)).fetchone()
        if row:
            return dict(row)
        return None
    finally:
        conn.close()

# Note: The users table uses email as PRIMARY KEY, not an id column
# Use get_user_by_email() instead for user lookups
