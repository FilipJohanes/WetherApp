# Database Schema Fixes - Summary

## Issues Found and Fixed

### 1. **lat/lon columns in wrong table**
**Problem:** The `users` table had `lat` and `lon` columns, but these should only exist in `weather_subscriptions` table.

**Fixed in:**
- ✅ `api.py` (line 137-152): Removed lat/lon from users table schema
- ✅ `services/subscription_service.py` (line 82): Updated query to use `ws.lat, ws.lon` instead of `u.lat, u.lon`  
- ✅ `services/weather_service.py` (line 343): Updated query to use `ws.lat, ws.lon` instead of `u.lat, u.lon`

### 2. **Obsolete functions referencing non-existent columns**
**Problem:** `services/user_service.py` had functions referencing columns that don't exist in the current schema.

**Fixed in:**
- ✅ Removed `set_user_personality()` - references non-existent `personality` and `id` columns
- ✅ Removed `create_password_reset()` - references non-existent `reset_token` and `reset_token_expiry` columns
- ✅ Removed `reset_password()` - references non-existent `reset_token_expiry` and `id` columns
- ✅ Removed `set_mfa_secret()` - references non-existent `mfa_secret` and `id` columns
- ✅ Removed `get_mfa_secret()` - references non-existent `mfa_secret` and `id` columns
- ✅ Removed `set_user_status()` - references non-existent `status` and `id` columns
- ✅ Removed `get_user()` - references non-existent `id` column

**Note:** Password reset functionality is properly handled via `password_reset_tokens` table in api.py

### 3. **API error handling improvement**
**Fixed in:**
- ✅ `api_client.py` (line 43): Fixed `response_data` scope issue and added better error logging

### 4. **Debug logging added**
**Added in:**
- ✅ `services/subscription_service.py`: Comprehensive logging for subscription creation
- ✅ `api.py`: Debug logging for subscription retrieval

## Current Valid Database Schema

### `users` table (email is PRIMARY KEY)
```sql
email TEXT PRIMARY KEY
username TEXT
nickname TEXT
password_hash TEXT
timezone TEXT DEFAULT 'UTC'
subscription_type TEXT DEFAULT 'free'
weather_enabled INTEGER DEFAULT 0
countdown_enabled INTEGER DEFAULT 0
reminder_enabled INTEGER DEFAULT 0
email_consent INTEGER DEFAULT 0
terms_accepted INTEGER DEFAULT 0
created_at TEXT NOT NULL
updated_at TEXT NOT NULL
```

### `weather_subscriptions` table (email is PRIMARY KEY + FOREIGN KEY)
```sql
email TEXT PRIMARY KEY
location TEXT NOT NULL
lat REAL NOT NULL
lon REAL NOT NULL
personality TEXT DEFAULT 'neutral'
language TEXT DEFAULT 'en'
last_sent_date TEXT
updated_at TEXT NOT NULL
FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE
```

### `countdowns` table
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
email TEXT NOT NULL
name TEXT NOT NULL
date TEXT NOT NULL
yearly INTEGER DEFAULT 0
message_before TEXT
message_after TEXT
created_at TEXT NOT NULL
FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE
```

### `password_reset_tokens` table
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
email TEXT NOT NULL
token TEXT NOT NULL UNIQUE
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
expires_at TIMESTAMP NOT NULL
used INTEGER DEFAULT 0
FOREIGN KEY (email) REFERENCES users(email)
```

## All Database Operations Verified

### INSERT operations ✅
- `services/user_service.py`: INSERT INTO users (email, username, nickname, password_hash, email_consent, terms_accepted, created_at, updated_at)
- `services/subscription_service.py`: INSERT INTO users (email, timezone, weather_enabled, created_at, updated_at)
- `services/subscription_service.py`: INSERT INTO weather_subscriptions (email, location, lat, lon, personality, language, updated_at)
- `services/countdown_service.py`: INSERT INTO users (email, username, timezone, weather_enabled, countdown_enabled, reminder_enabled, created_at, updated_at)
- `services/countdown_service.py`: INSERT INTO countdowns (email, name, date, yearly, message_before, message_after, created_at)
- `api.py`: INSERT INTO password_reset_tokens (email, token, expires_at)

### UPDATE operations ✅
- `api.py`: UPDATE users SET password_hash = ? WHERE email = ?
- `api.py`: UPDATE users SET nickname = ? WHERE email = ?
- `services/subscription_service.py`: UPDATE users SET timezone = ?, weather_enabled = 1, updated_at = ? WHERE email = ?
- `services/subscription_service.py`: UPDATE users SET weather_enabled = 0, updated_at = ? WHERE email = ?
- `services/countdown_service.py`: UPDATE users SET countdown_enabled = 1, updated_at = ? WHERE email = ?
- `services/countdown_service.py`: UPDATE users SET countdown_enabled = 0, updated_at = ? WHERE email = ?
- `api.py`: UPDATE password_reset_tokens SET used = 1 WHERE token = ?

### SELECT operations ✅
All SELECT queries verified to use only existing columns from correct tables.

## Migration Scripts Created

1. **`scripts/migrate_remove_user_latlon.py`**
   - Safely removes lat/lon columns from existing users table
   - Creates backup and migrates data

2. **`scripts/validate_database_schema.py`**
   - Validates database schema matches expectations
   - Reports any missing or extra columns
   - Run this after migration to verify

## Next Steps

1. Run migration on production database:
   ```bash
   python scripts/migrate_remove_user_latlon.py
   ```

2. Validate schema:
   ```bash
   python scripts/validate_database_schema.py
   ```

3. Test subscription flow:
   - Create new weather subscription
   - Check logs for successful save
   - Refresh page and verify subscription persists

## Environment Variables

Make sure these are set correctly in production .env:
- `WEB_APP_URL`: Should be set to your production domain (https://weather.bikesport-senec.sk)
- `APP_DB_PATH`: Database path
- `API_KEYS`: API authentication keys
- `BACKEND_API_URL`: URL for API backend
