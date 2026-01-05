# Production Deployment Checklist

Use this checklist to ensure smooth deployment to production.

## Pre-Deployment Verification

### Local Testing ✅
- [x] All 21 database tests pass
- [x] System check passes (no errors)
- [x] PyJWT dependency installed
- [x] Database schema validated
- [x] No lint/import errors

### Environment Configuration
- [ ] WEB_APP_URL set to production domain (https://weather.bikesport-senec.sk)
- [ ] EMAIL_ADDRESS configured for production SMTP
- [ ] EMAIL_PASSWORD configured (app password)
- [ ] JWT_SECRET_KEY set to secure random string
- [ ] FLASK_SECRET_KEY set to secure random string
- [ ] API_KEYS configured for weather API
- [ ] BACKEND_API_KEY configured (optional but recommended)

## Deployment Steps

### 1. Server Preparation
```bash
# Connect to production server
ssh pi@weather.bikesport-senec.sk

# Navigate to app directory
cd /path/to/reminderAPP

# Pull latest code
git pull origin main
```

### 2. Dependency Installation
```bash
# Activate virtual environment (if using)
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Verify PyJWT is installed
python -c "import jwt; print('PyJWT version:', jwt.__version__)"
```

### 3. Database Migration

**Option A: Fresh Installation (No Existing Data)**
```bash
# Initialize new database with correct schema
python scripts/init_db.py

# Verify schema
python scripts/validate_database_schema.py
```

**Option B: Migrate Existing Database**
```bash
# CRITICAL: Backup existing database first!
cp app.db app.db.backup.$(date +%Y%m%d_%H%M%S)

# Run migration to remove lat/lon from users table
python scripts/migrate_remove_user_latlon.py

# Validate schema is correct
python scripts/validate_database_schema.py

# If migration fails, restore backup:
# cp app.db.backup.YYYYMMDD_HHMMSS app.db
```

### 4. Configuration Verification
```bash
# Run system check
python scripts/system_check.py

# Expected output: "System is operational with 1 warnings"
# Warning about BACKEND_API_KEY is acceptable if not using API key auth
```

### 5. Test Database Operations
```bash
# Run comprehensive database tests
python -m pytest tests/test_database_operations.py -v

# Expected: 21 passed
```

### 6. Service Restart

**If using systemd:**
```bash
# Restart API backend
sudo systemctl restart dailybrief-api

# Restart web frontend
sudo systemctl restart dailybrief-web

# Check status
sudo systemctl status dailybrief-api
sudo systemctl status dailybrief-web

# View logs
sudo journalctl -u dailybrief-api -f
sudo journalctl -u dailybrief-web -f
```

**If running manually:**
```bash
# Kill existing processes
pkill -f "python api.py"
pkill -f "python web_app.py"

# Start API backend
nohup python api.py > logs/api.log 2>&1 &

# Start web frontend
nohup python web_app.py > logs/web.log 2>&1 &

# Verify processes running
ps aux | grep python
```

### 7. Functional Testing

**Test User Registration:**
```bash
curl -X POST https://weather.bikesport-senec.sk/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123!"}'
```

**Test Weather Subscription (via web interface):**
1. Navigate to https://weather.bikesport-senec.sk
2. Register a test account
3. Subscribe to weather updates
4. **CRITICAL:** Refresh the page
5. Verify subscription still shows (should NOT disappear)
6. Edit subscription and verify changes persist

**Test Countdown:**
1. Add a countdown event
2. Verify it appears in list
3. Refresh page
4. Verify countdown still shows

**Test Password Reset:**
1. Click "Forgot Password"
2. Enter test email
3. Check email for reset link
4. Verify link points to production domain (not localhost)

## Post-Deployment Validation

### Immediate Checks (5 minutes after deployment)
- [ ] Website loads at https://weather.bikesport-senec.sk
- [ ] User registration works
- [ ] Login/logout works
- [ ] Weather subscription persists after page refresh
- [ ] Countdown creation works
- [ ] Settings page loads correctly
- [ ] No errors in server logs

### Short-term Monitoring (24 hours)
- [ ] Scheduled emails sent successfully
- [ ] No database errors in logs
- [ ] API responses within normal range (< 1 second)
- [ ] No memory leaks or process crashes

### Database Health Check
```bash
# Check database integrity
sqlite3 app.db "PRAGMA integrity_check;"
# Expected output: ok

# Check table counts
python scripts/show_stats.py

# Verify foreign keys enabled
sqlite3 app.db "PRAGMA foreign_keys;"
# Expected output: 1
```

## Rollback Plan (If Issues Arise)

### Quick Rollback
```bash
# Stop services
sudo systemctl stop dailybrief-api dailybrief-web

# Restore previous code version
git checkout HEAD~1

# Restore database backup
cp app.db.backup.YYYYMMDD_HHMMSS app.db

# Restart services
sudo systemctl start dailybrief-api dailybrief-web
```

### Full Rollback
```bash
# Revert to previous stable release
git log --oneline  # Find previous stable commit
git checkout <commit-hash>

# Restore database
cp app.db.backup.YYYYMMDD_HHMMSS app.db

# Reinstall dependencies (in case they changed)
pip install -r requirements.txt

# Restart services
sudo systemctl restart dailybrief-api dailybrief-web
```

## Known Issues & Resolutions

### Issue: Subscriptions still disappearing
**Likely Cause:** Database not migrated properly
**Resolution:**
```bash
# Verify users table does NOT have lat/lon
sqlite3 app.db "PRAGMA table_info(users);"
# Should NOT show lat or lon columns

# If lat/lon exist, run migration again
python scripts/migrate_remove_user_latlon.py
```

### Issue: Import error "jwt could not be resolved"
**Likely Cause:** PyJWT not installed
**Resolution:**
```bash
pip install PyJWT>=2.8.0
```

### Issue: Password reset links point to localhost
**Likely Cause:** WEB_APP_URL not set in environment
**Resolution:**
```bash
# Add to .env file
echo "WEB_APP_URL=https://weather.bikesport-senec.sk" >> .env

# Restart services
sudo systemctl restart dailybrief-api dailybrief-web
```

### Issue: Foreign key constraint errors
**Likely Cause:** PRAGMA foreign_keys not enabled
**Resolution:** Already fixed in code - all connections now enable foreign keys

## Success Criteria

✅ **Deployment is successful if:**
1. All services start without errors
2. Website accessible at production URL
3. User registration/login works
4. Weather subscriptions persist after page refresh
5. No errors in logs for first 5 minutes
6. Scheduled jobs run successfully (check morning email delivery)

## Support Contacts

- **Developer:** (Your contact)
- **Server Admin:** (Server admin contact)
- **Documentation:** See SYSTEM_VALIDATION_REPORT.md

---

**Last Updated:** 2025  
**Version:** 1.0  
**Validated With:** Python 3.13.9, All 21 tests passing
