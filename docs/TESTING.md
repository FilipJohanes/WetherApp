# Testing System Documentation

## Overview

This testing system provides comprehensive verification of the Daily Brief Service MVP capabilities, including:

- Email-driven weather subscription service
- Web interface for subscription management
- Daily weather job with timezone-aware sending
- Countdown event tracking
- Multi-language and personality mode support

## Test Coverage

### Automated Tests (pytest)

#### 1. Database Schema Tests (`test_db_schema.py`)
- ✅ Subscribers table schema validation
- ✅ Countdowns table schema validation
- ✅ Inbox log table for deduplication
- ✅ Insert, update, delete operations
- ✅ UPSERT logic for subscriber updates
- ✅ Primary key constraints

#### 2. Subscription Flow Tests (`test_subscription_flow.py`)
- ✅ Add new subscriber
- ✅ Update existing subscriber location
- ✅ Update personality only (without re-geocoding)
- ✅ Update language only
- ✅ Delete subscriber
- ✅ Handle non-existent subscribers
- ✅ Multiple subscribers management

#### 3. Daily Weather Job Tests (`test_daily_weather_job.py`)
- ✅ Send emails at 5 AM local time
- ✅ Skip sending outside 5 AM hours
- ✅ Respect last_sent_date (no duplicates same day)
- ✅ Handle multiple timezones correctly
- ✅ Update last_sent_date after sending
- ✅ Include weather summary in email body
- ✅ Handle empty subscriber list gracefully

#### 4. Web App Routes Tests (`test_web_app_routes.py`)
- ✅ Home page loads
- ✅ Subscribe page (GET/POST)
- ✅ Subscribe with valid location
- ✅ Subscribe with invalid location (error handling)
- ✅ Update existing subscription
- ✅ Unsubscribe existing user
- ✅ Unsubscribe non-existent user
- ✅ Preview page with weather
- ✅ Stats page with aggregates
- ✅ API /api/check-email (subscribed/not subscribed)
- ✅ Input validation (SQL injection protection)
- ✅ Rate limiting configured

### Manual Test Scripts

#### 1. `scripts/test_local_daily_job.py`
**Purpose**: Simulate daily weather job execution at different times and timezones.

**Usage**:
```bash
python scripts/test_local_daily_job.py
```

**Features**:
- Creates temporary test database with sample subscribers
- Mocks SMTP/IMAP to avoid real email sending
- Simulates 5 AM in different timezones
- Displays email output in console
- Interactive scenario runner

**Scenarios tested**:
- Bratislava 5 AM (should send)
- Bratislava 3 PM (should NOT send)
- New York 5 AM (should send)
- Tokyo 5 AM (should send)

#### 2. `scripts/show_stats.py`
**Purpose**: Display comprehensive database statistics.

**Usage**:
```bash
python scripts/show_stats.py [db_path]
```

**Features**:
- Total subscriber count
- Language distribution with charts
- Personality distribution
- Timezone distribution
- Recent activity (last 10 updates)
- Email sending statistics
- Countdown event statistics
- Top locations

#### 3. `scripts/test_local_web_flow.py`
**Purpose**: Test complete web subscription flow without running server.

**Usage**:
```bash
python scripts/test_local_web_flow.py
```

**Features**:
- Uses Flask test client
- Creates temporary test database
- Mocks external API calls
- Tests complete user journey:
  1. Load home page
  2. Subscribe new user
  3. View preview
  4. Update subscription
  5. Check API
  6. Unsubscribe
  7. Verify unsubscription

## Installation

### 1. Install Dependencies

```bash
# Production dependencies
pip install -r requirements.txt

# Development and testing dependencies
pip install -r requirements-dev.txt
```

### 2. Set Environment Variables (for real runs)

```bash
# .env file
EMAIL_ADDRESS=your@email.com
EMAIL_PASSWORD=your_password
IMAP_HOST=imap.example.com
SMTP_HOST=smtp.example.com
FLASK_SECRET_KEY=your_secret_key_here

# Optional: Use test database
APP_DB_PATH=test_app.db
```

## Running Tests

### Quick Test (All Tests)

```bash
pytest -q
```

### Verbose Output

```bash
pytest -v
```

### Specific Test File

```bash
pytest tests/test_db_schema.py -v
pytest tests/test_subscription_flow.py -v
pytest tests/test_daily_weather_job.py -v
pytest tests/test_web_app_routes.py -v
```

### With Coverage Report

```bash
pytest --cov=services --cov=app --cov-report=html --cov-report=term
```

### Filter by Marker

```bash
pytest -m unit          # Only unit tests
pytest -m integration   # Only integration tests
pytest -m web          # Only web tests
```

## Running Manual Scripts

### Daily Job Simulation

```bash
python scripts/test_local_daily_job.py
```

**Expected Output**: Interactive prompts to run different time/timezone scenarios, with simulated email output displayed in console.

### Database Statistics

```bash
# Use default app.db
python scripts/show_stats.py

# Use specific database
python scripts/show_stats.py path/to/test.db
```

**Expected Output**: Formatted statistics with charts, distributions, and activity logs.

### Web Flow Test

```bash
python scripts/test_local_web_flow.py
```

**Expected Output**: Step-by-step test results showing HTTP status codes and API responses.

## Test Database Isolation

All tests use temporary databases to avoid polluting production data:

1. **Automated tests**: Each test function gets a fresh `test_db` fixture
2. **Manual scripts**: Create temporary databases with `.mkstemp()`
3. **Environment variable**: `APP_DB_PATH` controls which database to use

## Mocking Strategy

### External Services Mocked

1. **Geocoding** (`geocode_location`):
   - Returns predictable coordinates for test locations
   - Maps: Bratislava, New York, Tokyo, London

2. **Weather Forecast** (`get_weather_forecast`):
   - Returns consistent weather data
   - temp_max: 22.5°C, temp_min: 12.3°C, precipitation: 2.5mm

3. **Email Sending** (`send_email`):
   - Captures emails in list instead of sending
   - Allows verification of to/subject/body

4. **DateTime** (`datetime.now`):
   - Returns fixed time for time-dependent tests
   - Default: 2025-12-16 05:00:00

### Why Mock?

- ✅ **Deterministic**: Tests produce consistent results
- ✅ **Fast**: No network calls or real SMTP delays
- ✅ **Isolated**: No dependency on external services
- ✅ **Safe**: No real emails sent during testing

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: pytest -v --cov=services --cov=app
```

## Troubleshooting

### Tests Failing Due to Database Lock

**Problem**: SQLite database locked error

**Solution**: Ensure `test_db` fixture is properly scoped as `function` level, not `session`.

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'services'`

**Solution**: Tests automatically add parent directory to `sys.path`. Ensure you run pytest from project root.

### Mock Not Applied

**Problem**: Tests are making real API calls

**Solution**: Check that fixtures are applied to test functions:
```python
def test_something(mock_geocode, mock_weather_forecast):
    # Mocks are active here
```

### Flask CSRF Token Error

**Problem**: `CSRFError` in web tests

**Solution**: Tests automatically set `WTF_CSRF_ENABLED = False`. Ensure using `flask_test_client` fixture.

## MVP Checklist Coverage

### ✅ Email Engine
- [x] Command parsing (weather, DELETE, personality, language)
- [x] Subscription create/update
- [x] Unsubscribe (DELETE command)
- [x] Deduplication (inbox_log)
- [x] Daily sending at 5 AM local time
- [x] No duplicate sends same day
- [x] Weather summary generation
- [x] Personality modes (neutral, cute, brutal, emuska)
- [x] Multi-language support (EN/ES/SK)

### ✅ Web App
- [x] /subscribe route (GET/POST)
- [x] /unsubscribe route
- [x] /preview route
- [x] /stats route
- [x] /api/check-email endpoint
- [x] Input validation (SQL injection protection)
- [x] Rate limiting
- [x] CSRF protection

### ✅ Database
- [x] Schema initialization
- [x] Subscribers table with all fields
- [x] Countdowns table
- [x] Inbox log for deduplication
- [x] UPSERT logic
- [x] Timezone storage and handling

### ✅ Security
- [x] No credential leakage in logs
- [x] SQL injection prevention
- [x] Input sanitization
- [x] Rate limiting configured
- [x] CSRF tokens (web)

## Extending Tests

### Adding New Test

1. Create test file in `tests/` following naming convention `test_*.py`
2. Import fixtures from `conftest.py`
3. Write test functions with `test_` prefix
4. Use fixtures for database and mocking

Example:
```python
def test_my_feature(test_db, mock_config, mock_send_email):
    # Your test code
    assert expected == actual
```

### Adding New Mock

Edit `tests/conftest.py`:

```python
@pytest.fixture
def mock_my_service():
    def mock_fn(*args):
        return "mocked_result"
    
    with patch('module.my_service', side_effect=mock_fn):
        yield mock_fn
```

### Adding Manual Script

Create script in `scripts/` directory with shebang and docstring:

```python
#!/usr/bin/env python3
"""
Description of what the script does.
"""
# Implementation
```

## Performance

- **Test suite execution time**: ~5-10 seconds for all tests
- **Manual scripts**: 1-30 seconds depending on interactivity
- **Database operations**: In-memory or temporary files for speed

## Best Practices

1. **Isolation**: Each test is independent, no shared state
2. **Mocking**: Mock external services, never real API calls
3. **Cleanup**: Temporary databases are automatically removed
4. **Readability**: Clear test names describe what is being tested
5. **Assertions**: Use specific assertions with helpful messages

## Support

For issues or questions about the testing system:
1. Check this documentation
2. Review test code in `tests/` directory
3. Examine fixtures in `tests/conftest.py`
4. Run manual scripts with `-h` flag (if implemented)
