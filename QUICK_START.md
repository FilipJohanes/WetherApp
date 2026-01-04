# Quick Start Guide - New API Endpoints

## For Backend Developer (You)

### 1. Install Dependencies
```bash
cd c:\PythonProjects\WetherApp
pip install PyJWT>=2.8.0
# or
pip install -r requirements.txt
```

### 2. Configure Environment
Generate secure keys:
```python
import secrets
print("API_KEY:", secrets.token_urlsafe(32))
print("JWT_SECRET:", secrets.token_urlsafe(64))
```

Add to your `.env` file:
```env
API_KEYS=<paste_generated_api_key>
JWT_SECRET_KEY=<paste_generated_jwt_secret>
API_PORT=5001
APP_DB_PATH=app.db
```

### 3. Start API Server
```bash
python api.py
```

You should see:
```
🚀 Starting Daily Brief REST API
📊 Database: app.db
✅ Database initialized successfully
🔐 API Key authentication enabled
🔑 JWT authentication enabled for /api/v2/* endpoints
⏰ JWT token expiration: 168 hours
```

### 4. Test the API
```bash
# In another terminal:
python test_jwt_api.py
```

Update test credentials in `test_jwt_api.py` if needed:
```python
TEST_EMAIL = "your_test_user@example.com"
TEST_PASSWORD = "your_test_password"
```

### 5. Check Everything Works

Expected test output:
```
✅ PASS - health
✅ PASS - daily_brief
✅ PASS - weather
✅ PASS - countdowns
✅ PASS - nameday
✅ PASS - invalid_token

📊 Results: 6/6 tests passed
🎉 All tests passed!
```

---

## For Swift Developer

### 1. Get API Credentials
You'll need:
- **API Base URL**: `https://your-domain.com` (or `http://localhost:5001` for testing)
- **API Key**: (provided separately)

### 2. Read Documentation
Open [`API_DOCUMENTATION.md`](./API_DOCUMENTATION.md) for:
- Complete endpoint specifications
- Request/response examples
- Swift integration code
- Error handling guide

### 3. Implementation Steps

#### Step 1: Setup API Client
Use the `DailyBriefAPI` class from the documentation.

#### Step 2: Implement Login
```swift
api.login(email: email, password: password) { result in
    switch result {
    case .success(let token):
        // Token is automatically stored in api.jwtToken
        // Now you can call other endpoints
    case .failure(let error):
        // Handle error
    }
}
```

#### Step 3: Fetch Daily Brief
```swift
api.getDailyBrief { result in
    switch result {
    case .success(let dailyBrief):
        // Update UI with dailyBrief.weather, .countdowns, etc.
    case .failure(let error):
        // Handle error
    }
}
```

#### Step 4: Store Token Securely
```swift
import Security

// Save token to Keychain
let query: [String: Any] = [
    kSecClass as String: kSecClassGenericPassword,
    kSecAttrAccount as String: "jwt_token",
    kSecValueData as String: token.data(using: .utf8)!
]
SecItemAdd(query as CFDictionary, nil)
```

### 4. Test with Real Data

Test endpoints manually:
```bash
# Get token
curl -X POST http://localhost:5001/api/users/authenticate \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'

# Copy token from response, then:
curl http://localhost:5001/api/v2/daily-brief \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## API Endpoints Quick Reference

### Authentication
```
POST /api/users/authenticate
Headers: X-API-Key
Body: {email, password}
→ Returns: {token, expires_in}
```

### Get All Data (Recommended for app startup)
```
GET /api/v2/daily-brief
Headers: Authorization: Bearer <token>
→ Returns: Complete user data
```

### Get Specific Data
```
GET /api/v2/weather          # Weather + 7-day forecast
GET /api/v2/countdowns       # All countdowns with calculations
GET /api/v2/nameday          # Today's nameday
```

---

## Common Issues & Solutions

### Issue: "pip not recognized"
**Solution**: Use full Python path:
```bash
C:/PythonProjects/WetherApp/.venv/Scripts/python.exe -m pip install PyJWT
```

### Issue: "Invalid or missing API key"
**Solution**: 
1. Check `.env` file has `API_KEYS=...`
2. Restart API server after changing `.env`
3. Use correct API key in request headers

### Issue: "Token has expired"
**Solution**: 
- Get new token by calling `/api/users/authenticate` again
- Tokens expire after 7 days
- Implement auto-refresh in your app

### Issue: "User not found"
**Solution**: 
- Make sure user exists in database
- Check email is correct (lowercase)
- User must have completed registration

### Issue: "Weather subscription not found"
**Solution**: 
- User needs to set up weather subscription first
- Use web interface or `/api/weather/subscriptions` endpoint

---

## Rate Limits

| Endpoint | Limit | Notes |
|----------|-------|-------|
| `/api/users/authenticate` | 20/hour | Login attempts |
| `/api/v2/*` (all v2 endpoints) | 50/hour | Combined limit |

**Best Practice**: 
- Cache responses in your app
- Only refresh when needed (e.g., pull-to-refresh)
- Implement exponential backoff for retries

---

## Example Request/Response

### Request:
```http
GET /api/v2/weather HTTP/1.1
Host: localhost:5001
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Response:
```json
{
  "success": true,
  "data": {
    "location": "Bratislava",
    "today": {
      "temp_max": 25.5,
      "temp_min": 15.2,
      "condition": "sunny"
    },
    "week_forecast": [
      {
        "day_name": "Monday",
        "temp_max": 22.0,
        "temp_min": 14.0,
        "condition": "cloudy"
      }
    ]
  }
}
```

---

## Need Help?

1. **API Documentation**: See [`API_DOCUMENTATION.md`](./API_DOCUMENTATION.md)
2. **Test Script**: Run `python test_jwt_api.py`
3. **Error Logs**: Check API server console output
4. **Database Issues**: Check `app.db` exists and is accessible

---

## Next Steps

### Backend:
- ✅ API endpoints ready
- ⏳ Deploy to production server
- ⏳ Set up HTTPS/SSL
- ⏳ Configure production `.env`

### Frontend (Swift):
- ⏳ Implement authentication
- ⏳ Create data models
- ⏳ Build UI components
- ⏳ Test with real data
- ⏳ Implement caching
- ⏳ Handle token refresh

---

## Security Checklist

Before going to production:

- [ ] Generate strong API_KEYS (32+ characters)
- [ ] Generate strong JWT_SECRET_KEY (64+ characters)
- [ ] Never commit `.env` file to git
- [ ] Use HTTPS in production
- [ ] Set up proper CORS if needed
- [ ] Monitor rate limit abuse
- [ ] Implement proper logging
- [ ] Set up error tracking (e.g., Sentry)

---

## Success! 🎉

You now have a production-ready API with:
- ✅ JWT authentication
- ✅ Structured JSON responses
- ✅ 7-day weather forecast
- ✅ User data isolation
- ✅ Rate limiting
- ✅ Complete documentation
- ✅ Test suite

Ready for mobile app integration!
