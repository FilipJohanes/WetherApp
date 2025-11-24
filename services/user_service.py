
import sqlite3
import hashlib
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional
import bcrypt

# Update user personality
def set_user_personality(user_id: int, personality: str):
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("UPDATE users SET personality = ?, updated_at = ? WHERE id = ?", (personality, datetime.utcnow().isoformat(), user_id))
        conn.commit()
    finally:
        conn.close()
"""
User Service Module
Handles registration, authentication, password reset, MFA, and status management for user accounts.
"""
DB_PATH = "app.db"

# Password hashing helpers

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())

# User registration

def register_user(email: str, password: str) -> bool:
    password_hash = hash_password(password)
    now = datetime.utcnow().isoformat()
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("""
            INSERT INTO users (email, password_hash, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        """, (email, password_hash, now, now))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Email already exists
    finally:
        conn.close()

# User authentication

def authenticate_user(email: str, password: str) -> Optional[int]:
    conn = sqlite3.connect(DB_PATH)
    try:
        row = conn.execute("SELECT id, password_hash, status FROM users WHERE email = ?", (email,)).fetchone()
        if not row:
            return None
        user_id, password_hash, status = row
        if status != "active":
            return None
        if verify_password(password, password_hash):
            return user_id
        return None
    finally:
        conn.close()

# Password reset

def create_password_reset(email: str) -> Optional[str]:
    token = secrets.token_urlsafe(32)
    expiry = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    conn = sqlite3.connect(DB_PATH)
    try:
        result = conn.execute("UPDATE users SET reset_token = ?, reset_token_expiry = ? WHERE email = ?", (token, expiry, email))
        conn.commit()
        if result.rowcount:
            return token
        return None
    finally:
        conn.close()

def reset_password(token: str, new_password: str) -> bool:
    now = datetime.utcnow().isoformat()
    password_hash = hash_password(new_password)
    conn = sqlite3.connect(DB_PATH)
    try:
        row = conn.execute("SELECT id, reset_token_expiry FROM users WHERE reset_token = ?", (token,)).fetchone()
        if not row:
            return False
        user_id, expiry = row
        if expiry < now:
            return False
        conn.execute("UPDATE users SET password_hash = ?, reset_token = NULL, reset_token_expiry = NULL, updated_at = ? WHERE id = ?", (password_hash, now, user_id))
        conn.commit()
        return True
    finally:
        conn.close()

# MFA setup and verification (TOTP placeholder)
def set_mfa_secret(user_id: int, secret: str):
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("UPDATE users SET mfa_secret = ? WHERE id = ?", (secret, user_id))
        conn.commit()
    finally:
        conn.close()

def get_mfa_secret(user_id: int) -> Optional[str]:
    conn = sqlite3.connect(DB_PATH)
    try:
        row = conn.execute("SELECT mfa_secret FROM users WHERE id = ?", (user_id,)).fetchone()
        return row[0] if row else None
    finally:
        conn.close()

# User status management
def set_user_status(user_id: int, status: str):
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("UPDATE users SET status = ?, updated_at = ? WHERE id = ?", (status, datetime.utcnow().isoformat(), user_id))
        conn.commit()
    finally:
        conn.close()

def get_user_by_email(email: str):
    conn = sqlite3.connect(DB_PATH)
    try:
        return conn.execute("SELECT id, email, status FROM users WHERE email = ?", (email,)).fetchone()
    finally:
        conn.close()

# Utility for future premium features
def get_user(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    try:
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    finally:
        conn.close()
