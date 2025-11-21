
# app.py Function and Class Map (Detailed Backup Documentation)

## Classes

### SafeStreamHandler(logging.StreamHandler)
- **Purpose:** Custom logging handler to safely handle Unicode characters (emojis, international text) in logs.
- **Method:**
	- `emit(record)`: Emits log records, falls back to ASCII if UnicodeEncodeError occurs.
- **Used for:** Ensuring logs are readable and error-free regardless of character encoding.

### EmailMessageInfo(NamedTuple)
- **Purpose:** Represents normalized email message data for processing.
- **Fields:**
	- `uid`: Unique identifier for deduplication
	- `from_email`: Sender's email address
	- `subject`: Email subject
	- `plain_text_body`: Extracted plain text body
	- `date`: Date/time received
- **Used for:** Passing email data between IMAP fetch and command processing.

### Config
- **Purpose:** Loads and validates configuration from environment variables (email, IMAP/SMTP, timezone, language).
- **Methods:**
	- `__init__()`: Loads all required config values, exits if missing.
	- `_get_env(key)`: Helper to fetch required env variable or exit.
- **Used for:** Centralized config for all service operations.

## Functions

### Signal Handling
- `signal_handler(signum, frame)`
	- **Purpose:** Handles graceful shutdown on Ctrl+C or termination signals.
	- **Side effects:** Shuts down scheduler, logs shutdown, exits process.
	- **Used for:** Service reliability and clean exit.

### Environment & Database
- `load_env()`
	- **Purpose:** Loads config from environment, sets global timezone.
	- **Returns:** Config object
	- **Used for:** All service startup and email operations.

- `init_db(path="app.db")`
	- **Purpose:** Initializes SQLite database and tables (subscribers, reminders, inbox_log).
	- **Side effects:** Creates/updates DB schema, handles upgrades.
	- **Used for:** Ensuring DB is ready for all features.

### Email Handling
- `imap_fetch_unseen(config)`
	- **Purpose:** Fetches unseen emails from IMAP inbox.
	- **Returns:** List of EmailMessageInfo
	- **Used for:** Inbox polling job, command processing.

- `_extract_plain_text(email_message)`
	- **Purpose:** Extracts and cleans plain text from email (removes signatures, reply chains).
	- **Returns:** String (plain text body)
	- **Used for:** Parsing commands from inbound emails.

- `mark_seen(config, uid)`
	- **Purpose:** Placeholder for marking emails as seen (not implemented, deduplication used instead).

- `send_email(config, to, subject, body, dry_run=False)`
	- **Purpose:** Sends email via SMTP (TLS/SSL supported).
	- **Returns:** True if sent, False if error
	- **Used for:** All outbound notifications, confirmations, test emails.

### Command Parsing & Processing
- `parse_plaintext(body)`
	- **Purpose:** Parses email body to determine command type (weather, delete, personality, language, calendar).
	- **Returns:** Dict with command and parameters
	- **Used for:** Routing inbound email commands.

- `load_weather_messages(file_path=None, language="en")`
	- **Purpose:** Loads weather message templates for all personality modes and languages.
	- **Returns:** Dict of condition → personality → message
	- **Used for:** Generating personalized weather summaries.

- `_get_default_weather_messages()`
	- **Purpose:** Provides fallback weather messages if config file is missing.
	- **Returns:** Dict of default messages

- `detect_weather_condition(weather)`
	- **Purpose:** Analyzes weather data to determine main condition (rain, sunny, heatwave, etc.).
	- **Returns:** String (condition)
	- **Used for:** Selecting correct message and advice.

- `get_weather_message(condition, personality, messages=None, language="en")`
	- **Purpose:** Gets weather message for given condition/personality/language.
	- **Returns:** String (message)

- `geocode_location(location)`
	- **Purpose:** Geocodes location string to lat/lon using Open-Meteo API.
	- **Returns:** Tuple (lat, lon, display_name) or None
	- **Used for:** Subscribing users, weather lookups.

- `get_weather_forecast(lat, lon, timezone_name)`
	- **Purpose:** Fetches weather forecast for given coordinates/timezone from Open-Meteo API.
	- **Returns:** Dict of weather data or None

- `generate_weather_summary(weather, location, personality='neutral', language='en')`
	- **Purpose:** Generates full weather summary (temperature, rain, wind, message, clothing advice).
	- **Returns:** String (summary)

- `_generate_clothing_advice(temp_max, precip_prob, precip_sum, wind_speed, personality)`
	- **Purpose:** Generates clothing advice based on weather and personality mode.
	- **Returns:** String (advice)

### Command Handlers
- `handle_weather_command(config, from_email, location=None, is_delete=False, personality=None, language=None, dry_run=False)`
	- **Purpose:** Handles weather subscription, update, or deletion for a user.
	- **Side effects:** Updates DB, sends confirmation email.
	- **Used for:** Main user interaction via email.

- `handle_personality_command(config, from_email, mode, dry_run=False)`
	- **Purpose:** Changes personality mode for a subscriber.
	- **Side effects:** Updates DB, sends sample email.

- `handle_language_command(config, from_email, language, dry_run=False)`
	- **Purpose:** Changes language for a subscriber.
	- **Side effects:** Updates DB, sends sample email.

- `handle_calendar_command(config, from_email, fields, dry_run=False)`
	- **Purpose:** Schedules calendar reminders (currently disabled in main jobs).
	- **Side effects:** Inserts reminders in DB, sends confirmation email.

- `delete_all_reminders(config, from_email, dry_run=False)`
	- **Purpose:** Deletes all pending reminders for a user.
	- **Side effects:** Updates DB, sends confirmation email.

- `_get_usage_footer()`
	- **Purpose:** Returns usage instructions for all supported commands.
	- **Returns:** String (footer)

### Scheduled Jobs
- `run_daily_weather_job(config, dry_run=False)`
	- **Purpose:** Sends daily weather forecast to all subscribers at 05:00 local time.
	- **Side effects:** Loops through subscribers, sends emails.
	- **Scheduled by:** APScheduler (main entrypoint)

- `run_due_reminders_job(config, dry_run=False)`
	- **Purpose:** Sends due calendar reminders (currently disabled in main jobs).
	- **Side effects:** Loops through reminders, sends emails, updates DB.

- `process_inbound_email(config, msg, dry_run=False)`
	- **Purpose:** Processes a single inbound email (deduplication, command parsing, routing).
	- **Side effects:** Updates inbox_log, calls appropriate handler, sends emails.

- `should_process_email(msg)`
	- **Purpose:** Filters out system/automated emails, short/empty bodies, encoded subjects.
	- **Returns:** True if user email, False otherwise

- `check_inbox_job(config, dry_run=False)`
	- **Purpose:** Polls inbox for new messages, processes each valid email.
	- **Scheduled by:** APScheduler (every minute)

### CLI Utilities
- `list_subscribers()`
	- **Purpose:** Prints all current weather subscribers to console.
	- **Used for:** CLI inspection/debugging.

- `list_reminders()`
	- **Purpose:** Prints all pending reminders to console.
	- **Used for:** CLI inspection/debugging.

- `send_test_email(config, to_email)`
	- **Purpose:** Sends a test email to verify SMTP config.
	- **Used for:** CLI testing and diagnostics.

- `create_readme_if_missing()`
	- **Purpose:** Creates README.md with service info if missing.
	- **Side effects:** Writes file, logs creation.

### Main Entrypoint
- `main()`
	- **Purpose:** Main application entry point. Handles CLI args, DB init, config loading, job scheduling, and service startup.
	- **Side effects:** Starts APScheduler, runs jobs, handles signals.

---

**Notes:**
- All email, weather, and reminder logic is modular and can be refactored into services.
- CLI commands are handled via argparse in `main()`.
- Scheduled jobs use APScheduler for reliability and timing.
- All database operations use SQLite and are wrapped in try/finally for safety.
- The file is designed for extensibility and can be split into service modules for easier maintenance.

This backup document provides a comprehensive, detailed map of all classes and functions in app.py, including their purpose, parameters, return values, usage, and dependencies. Use this as a reference for restructuring, rebasing, or refactoring.
