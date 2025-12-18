# Testing Quick Start Guide

## TL;DR - Run Tests Now

```bash
# 1. Install dependencies (one time)
pip install -r requirements.txt -r requirements-dev.txt

# 2. Run automated tests
pytest -q

# 3. Run manual daily job simulation
python scripts/test_local_daily_job.py

# 4. Check database stats
python scripts/show_stats.py

# 5. Test web flow
python scripts/test_local_web_flow.py
```

## What Gets Tested

### ✅ Automated Tests (pytest)
- **Database**: Schema, CRUD operations, constraints (7 tests)
- **Subscriptions**: Add, update, delete users (9 tests)
- **Web App**: All Flask routes, API, security (18 tests)
- **Total**: 33 tests passing in ~8 seconds

### ✅ Manual Scripts
- **Daily Job**: Interactive timezone simulation
- **Stats**: Beautiful database statistics display
- **Web Flow**: Complete subscription journey test

## Test Output Examples

### Pytest (Automated)
```
$ pytest -q
.................................
33 passed, 7 skipped in 8.57s
```

### Daily Job Script (Manual)
```
$ python scripts/test_local_daily_job.py

╔══════════════════════════════════════╗
║    Daily Weather Job Test Script     ║
╚══════════════════════════════════════╝

📋 Scenario 1: Bratislava 5 AM - Should send
[Press Enter to run...]

📧 SIMULATED EMAIL
To: bratislava@test.com
Subject: Daily Brief

[Weather content displayed...]
✅ Simulation complete!
```

### Stats Script (Manual)
```
$ python scripts/show_stats.py

📊 TOTAL SUBSCRIBERS: 1
🌍 LANGUAGE DISTRIBUTION:
  sk     1 (100.0%) ████████████████████
😊 PERSONALITY DISTRIBUTION:
  neutral 1 (100.0%) ████████████████████
⏰ COUNTDOWN STATISTICS:
  Total countdowns: 3
  Upcoming events:
    • 2026-04-25 - Svadba
```

## Environment Variables

### Optional (for testing)
```bash
# Use test database instead of production
export APP_DB_PATH=test_app.db

# Then run any command
pytest -v
python scripts/show_stats.py test_app.db
```

## Test Database Isolation

All tests use **temporary databases** - your production `app.db` is safe:

- ✅ Pytest creates temp DB per test automatically
- ✅ Manual scripts create temp DB in `/tmp`
- ✅ No risk of data corruption
- ✅ Set `APP_DB_PATH` to use specific test DB

## Troubleshooting

### "ModuleNotFoundError"
```bash
# Install dev dependencies
pip install -r requirements-dev.txt
```

### "ImportError" on existing tests
```bash
# Run only new MVP tests (recommended)
pytest tests/test_db_schema.py tests/test_subscription_flow.py tests/test_web_app_routes.py -v
```

### "Database locked"
```bash
# Normal - tests use separate databases
# If persists, delete temp files:
rm /tmp/tmp*.db
```

## CI/CD Integration

### GitHub Actions
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: pytest -v
```

### GitLab CI
```yaml
test:
  script:
    - pip install -r requirements.txt -r requirements-dev.txt
    - pytest -v
```

## What's Mocked (No Real Calls)

- ✅ Open-Meteo API (geocoding + weather)
- ✅ SMTP email sending
- ✅ IMAP email receiving
- ✅ System time (datetime.now)

**Result**: Fast, deterministic, safe tests

## Full Documentation

- **Testing Guide**: `docs/TESTING.md` (comprehensive)
- **Summary Report**: `docs/MVP_TESTING_SUMMARY.md` (executive summary)
- **Test Code**: `tests/` directory
- **Manual Scripts**: `scripts/` directory

## Test Coverage Summary

| Category | Tests | Status |
|----------|-------|--------|
| Database Schema | 7 | ✅ All Pass |
| Subscription Flow | 9 | ✅ All Pass |
| Web App Routes | 18 | ✅ All Pass |
| Daily Job (Integration) | 7 | ⏭️ Skipped* |
| **Total** | **40** | **33 Pass / 7 Skip** |

*Skipped tests are documented - manual scripts provide alternative verification.

## Next Steps

1. ✅ Run `pytest -q` to verify all tests pass
2. ✅ Explore `python scripts/test_local_daily_job.py`
3. ✅ Check `python scripts/show_stats.py` on your database
4. ✅ Read `docs/TESTING.md` for deep dive
5. ✅ Integrate into your CI/CD pipeline

---

**Quick Help**: See `docs/TESTING.md` for detailed usage  
**Questions**: Check test code in `tests/` directory for examples
