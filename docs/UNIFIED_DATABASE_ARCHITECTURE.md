# Unified Database Architecture

## Overview

The application now uses a **unified database schema** where all user data is centralized in a master `users` table, with module-specific data stored in separate tables that reference the master table via foreign keys.

## Design Principles

1. **Master User Registry**: Single source of truth for all users
2. **Module Independence**: Each module has its own table, can be added/removed without affecting others
3. **Foreign Key Integrity**: All module tables reference the master `users` table
4. **Enable/Disable Flags**: Binary flags in master table control which modules are active for each user
5. **Extensibility**: New modules can be added by:
   - Adding a new `[module]_enabled` column to `users` table
   - Creating a new `[module]_subscriptions` or similar table with FK to users

## Database Schema

### Master Table: `users`

Central registry for all users across all modules.

```sql
CREATE TABLE users (
    email TEXT PRIMARY KEY,              -- Unique identifier
    username TEXT,                        -- Optional username
    password_hash TEXT,                   -- For authenticated features (nullable)
    timezone TEXT DEFAULT 'UTC',          -- User's timezone
    lat REAL,                            -- User's latitude (shared across modules)
    lon REAL,                            -- User's longitude (shared across modules)
    subscription_type TEXT DEFAULT 'free', -- Future: premium features
    weather_enabled INTEGER DEFAULT 0,    -- Weather module active flag
    countdown_enabled INTEGER DEFAULT 0,  -- Countdown module active flag
    reminder_enabled INTEGER DEFAULT 0,   -- Reminder module active flag
    created_at TEXT NOT NULL,            -- Account creation timestamp
    updated_at TEXT NOT NULL             -- Last modification timestamp
)
```

**Indexes:**
- `idx_users_weather` on `weather_enabled` (partial index for active weather users)
- `idx_users_countdown` on `countdown_enabled` (partial index for active countdown users)
- `idx_users_reminder` on `reminder_enabled` (partial index for active reminder users)

### Module Table: `weather_subscriptions`

Weather-specific subscription data.

```sql
CREATE TABLE weather_subscriptions (
    email TEXT PRIMARY KEY,              -- FK to users.email
    location TEXT NOT NULL,              -- Human-readable location name
    personality TEXT DEFAULT 'neutral',  -- Weather tone (cute, brutal, neutral, emuska)
    language TEXT DEFAULT 'en',          -- Language code (en, es, sk)
    last_sent_date TEXT,                 -- Last daily email sent date
    updated_at TEXT NOT NULL,            -- Last modification
    FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE
)
```

### Module Table: `countdowns`

Countdown events for users.

```sql
CREATE TABLE countdowns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,                 -- FK to users.email
    name TEXT NOT NULL,                  -- Event name
    date TEXT NOT NULL,                  -- Event date (YYYY-MM-DD)
    yearly INTEGER DEFAULT 0,            -- Recurring yearly flag
    message_before TEXT,                 -- Custom message before event
    message_after TEXT,                  -- Custom message after event
    created_at TEXT NOT NULL,            -- Creation timestamp
    FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE
)
```

**Indexes:**
- `idx_countdowns_email` on `email`

### Module Table: `reminders`

Calendar reminders for users.

```sql
CREATE TABLE reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,                 -- FK to users.email
    message TEXT NOT NULL,               -- Reminder message
    first_run_at TEXT NOT NULL,          -- When to send first reminder
    remaining_repeats INTEGER NOT NULL,  -- Number of repetitions left
    last_sent_at TEXT,                   -- Last sent timestamp
    created_at TEXT NOT NULL,            -- Creation timestamp
    FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE
)
```

**Indexes:**
- `idx_reminders_email_time` on `(email, first_run_at)`

### Support Table: `inbox_log`

Email deduplication log (no FK, independent).

```sql
CREATE TABLE inbox_log (
    uid TEXT PRIMARY KEY,                -- Email UID
    from_email TEXT NOT NULL,            -- Sender email
    received_at TEXT NOT NULL,           -- Received timestamp
    subject TEXT,                        -- Email subject
    body_hash TEXT                       -- Body hash for deduplication
)
```

## Migration from Old Schema

The migration script (`migrate_unified_db.py`) handles:

1. **Data consolidation**: Merges data from old `subscribers`, `weather`, and `users` tables
2. **User creation**: Creates master user records with appropriate module flags
3. **Module data migration**: Moves weather and countdown data to new tables
4. **Foreign key setup**: Establishes relationships between tables
5. **Index creation**: Creates performance indexes
6. **Backup**: Creates timestamped backup of old database

**Migration executed**: December 16, 2025
**Backup location**: `app_backup_20251216_154817.db`

## Code Architecture Changes

### Services Updated

1. **`services/subscription_service.py`**
   - `add_or_update_subscriber()`: Creates user if not exists, enables weather module
   - `delete_subscriber()`: Removes weather subscription, disables weather module
   - `get_subscriber()`: Joins users and weather_subscriptions tables

2. **`services/countdown_service.py`**
   - `add_countdown()`: Enables countdown module when adding events
   - `delete_countdown()`: Disables countdown module if no events remain
   - No longer needs `init_countdown_db()` (handled by main `init_db()`)

3. **`services/weather_service.py`**
   - `list_subscribers()`: Joins users and weather_subscriptions with enable flag check

4. **`services/email_service.py`**
   - `run_daily_job()`: Queries unified schema with LEFT JOINs for module data

### Application Updates

1. **`app.py`**
   - `init_db()`: Creates all tables including module tables in one place
   - Removed separate `init_countdown_db()` call

2. **`web_app.py`**
   - All subscriber queries updated to use unified schema
   - Uses service layer functions instead of direct SQL where possible
   - Stats endpoint updated to join tables

## Benefits of Unified Schema

### 1. **Modularity**
- Adding/removing modules doesn't affect other modules
- Each module has clean separation of concerns
- Module-specific columns don't clutter master table

### 2. **Data Integrity**
- Foreign keys enforce referential integrity
- Cascade deletes prevent orphaned records
- Master table ensures user uniqueness

### 3. **Performance**
- Partial indexes on enable flags optimize queries
- Module tables only contain active users' data
- Efficient joins using indexed foreign keys

### 4. **Maintainability**
- Clear ownership of data (master vs module-specific)
- Easy to understand which table contains what data
- Consistent patterns for new modules

### 5. **Future Extensions**

Easy to add new modules:

```sql
-- Add enable flag to master table
ALTER TABLE users ADD COLUMN new_module_enabled INTEGER DEFAULT 0;

-- Create module table
CREATE TABLE new_module_subscriptions (
    email TEXT PRIMARY KEY,
    module_specific_data TEXT,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE
);

-- Add index
CREATE INDEX idx_users_new_module ON users(new_module_enabled) 
WHERE new_module_enabled = 1;
```

## Usage Patterns

### Adding a User with Weather Subscription

```python
from services.subscription_service import add_or_update_subscriber

add_or_update_subscriber(
    email='user@example.com',
    location='Prague, Czech Republic',
    lat=50.0755,
    lon=14.4378,
    personality='cute',
    language='en',
    timezone='Europe/Prague'
)
# Creates user in master table with weather_enabled=1
# Creates weather subscription record
```

### Adding a Countdown for User

```python
from services.countdown_service import add_countdown, CountdownEvent

event = CountdownEvent(
    name='Birthday',
    date='2025-12-25',
    yearly=True,
    email='user@example.com',
    message_before='Days until birthday: {days}'
)
add_countdown(event)
# Enables countdown_enabled flag in master table
# Creates countdown record
```

### Querying Active Users for Daily Job

```python
conn.execute("""
    SELECT 
        u.email, u.timezone, u.lat, u.lon,
        u.weather_enabled, u.countdown_enabled, u.reminder_enabled,
        ws.location, ws.personality, ws.language
    FROM users u
    LEFT JOIN weather_subscriptions ws ON u.email = ws.email
    WHERE (u.weather_enabled = 1 OR u.countdown_enabled = 1 OR u.reminder_enabled = 1)
""")
```

## Testing

All tests updated to work with unified schema:
- `tests/conftest.py`: Removed redundant `init_countdown_db()` call
- `scripts/test_local_*.py`: Updated to use single `init_db()`

Migration verified with:
- 10 users migrated successfully
- 9 weather subscriptions preserved
- 4 countdowns preserved
- All foreign keys valid
- All indexes created

## Backup and Recovery

**Current backup**: `app_backup_20251216_154817.db`

To restore old schema (if needed):
```bash
cp app_backup_20251216_154817.db app.db
# Then revert code changes or re-run old version
```

## Notes

- The migration script preserves all data integrity
- Module enable flags automatically set based on existing subscriptions
- Timezone and coordinates pulled from best available source during migration
- Foreign keys are enforced (`PRAGMA foreign_keys = ON`)
- All timestamps use ISO 8601 format
