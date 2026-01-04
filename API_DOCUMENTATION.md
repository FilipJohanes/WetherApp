# DailyBrief API Documentation - Version 2 (Mobile Apps)

## Overview

This documentation covers the new JWT-protected API endpoints designed for mobile applications (iOS/Android). These endpoints return structured JSON data suitable for app interfaces.

**Base URL**: `https://your-api-domain.com` (or `http://localhost:5001` for development)

## Authentication Flow

### 1. API Key Requirement
All requests require an API key in the headers:
```
X-API-Key: your_api_key_here
```

### 2. User Authentication (Get JWT Token)

**Endpoint**: `POST /api/users/authenticate`

**Headers**:
```
X-API-Key: your_api_key_here
Content-Type: application/json
```

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "user_password"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "user": {
    "email": "user@example.com",
    "username": "username",
    "timezone": "Europe/Bratislava"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 604800
}
```

**Token expires in**: 7 days (604800 seconds)

### 3. Using JWT Token

For all `/api/v2/*` endpoints, include the JWT token in the Authorization header:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## API Endpoints (Version 2)

All v2 endpoints:
- Are protected with JWT authentication
- Return structured JSON data
- Have a combined rate limit of **50 requests per hour per user**
- Only return data for the authenticated user

---

### Get Daily Brief

**Endpoint**: `GET /api/v2/daily-brief`

**Description**: Get complete daily brief with all enabled modules (weather, countdowns, namedays)

**Headers**:
```
Authorization: Bearer <jwt_token>
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "user": {
      "email": "user@example.com",
      "username": "john_doe",
      "nickname": "John",
      "timezone": "Europe/Bratislava",
      "language": "en",
      "personality": "neutral"
    },
    "modules_enabled": {
      "weather": true,
      "countdown": true,
      "reminder": false
    },
    "weather": {
      "location": "Bratislava",
      "coordinates": {
        "lat": 48.1486,
        "lon": 17.1077
      },
      "timezone": "Europe/Bratislava",
      "today": {
        "temp_max": 25.5,
        "temp_min": 15.2,
        "precipitation_sum": 2.5,
        "precipitation_probability": 60,
        "wind_speed_max": 18.5,
        "condition": "rainy"
      },
      "week_forecast": [
        {
          "date": "2026-01-05",
          "day_name": "Monday",
          "temp_max": 22.0,
          "temp_min": 14.0,
          "precipitation_sum": 0.5,
          "precipitation_probability": 20,
          "wind_speed_max": 12.0,
          "condition": "sunny"
        }
        // ... 6 more days
      ],
      "summary_text": "Today's weather for Bratislava:\n\n🌡️ Temperature: High 25.5°C / Low 15.2°C..."
    },
    "countdowns": [
      {
        "name": "Birthday",
        "date": "2026-06-15",
        "yearly": true,
        "days_left": 162,
        "next_occurrence": "2026-06-15",
        "is_past": false,
        "message": "Days to Birthday: 162"
      }
    ],
    "nameday": {
      "date": "2026-01-04",
      "day_name": "Sunday",
      "names": "John, Jane",
      "message": "Today celebrates: John, Jane",
      "language": "en"
    },
    "reminders": [],
    "generated_at": "2026-01-04T10:30:00+01:00"
  }
}
```

---

### Get Weather Data

**Endpoint**: `GET /api/v2/weather`

**Description**: Get structured weather data including today's weather and 7-day forecast

**Headers**:
```
Authorization: Bearer <jwt_token>
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "location": "Bratislava",
    "coordinates": {
      "lat": 48.1486,
      "lon": 17.1077
    },
    "timezone": "Europe/Bratislava",
    "today": {
      "temp_max": 25.5,
      "temp_min": 15.2,
      "precipitation_sum": 2.5,
      "precipitation_probability": 60,
      "wind_speed_max": 18.5,
      "condition": "rainy"
    },
    "week_forecast": [
      {
        "date": "2026-01-05",
        "day_name": "Monday",
        "temp_max": 22.0,
        "temp_min": 14.0,
        "precipitation_sum": 0.5,
        "precipitation_probability": 20,
        "wind_speed_max": 12.0,
        "condition": "sunny"
      }
      // ... continues for 7 days
    ],
    "summary_text": "Today's weather for Bratislava:\n\n🌡️ Temperature..."
  }
}
```

**Weather Conditions**: `sunny`, `cloudy`, `rainy`, `snowing`, `thunderstorm`, `foggy`, `windy`, `hot`, `cold`, `mild`, `heatwave`, `blizzard`, `freezing`, `sunny_hot`, `cold_windy`, `rainy_cold`, `heavy_rain`, `humid`, `dry`, `default`

---

### Get Countdowns

**Endpoint**: `GET /api/v2/countdowns`

**Description**: Get all user's countdowns with calculated days remaining

**Headers**:
```
Authorization: Bearer <jwt_token>
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": [
    {
      "name": "Birthday",
      "date": "2026-06-15",
      "yearly": true,
      "days_left": 162,
      "next_occurrence": "2026-06-15",
      "is_past": false,
      "message": "Days to Birthday: 162"
    },
    {
      "name": "Project Deadline",
      "date": "2026-01-20",
      "yearly": false,
      "days_left": 16,
      "next_occurrence": "2026-01-20",
      "is_past": false,
      "message": "Days to Project Deadline: 16"
    }
  ]
}
```

---

### Get Nameday

**Endpoint**: `GET /api/v2/nameday`

**Description**: Get nameday information for today (or specified date) in user's language

**Headers**:
```
Authorization: Bearer <jwt_token>
```

**Query Parameters** (optional):
- `date`: ISO format date (YYYY-MM-DD) - defaults to today

**Examples**:
- `GET /api/v2/nameday` - Get today's nameday
- `GET /api/v2/nameday?date=2026-12-25` - Get nameday for specific date

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "date": "2026-01-04",
    "day_name": "Sunday",
    "names": "John, Jane",
    "message": "Today celebrates: John, Jane",
    "language": "en"
  }
}
```

**Response when nameday not supported**:
```json
{
  "success": true,
  "data": null,
  "message": "Nameday not supported for language: en"
}
```

---

## Error Responses

### 401 Unauthorized
```json
{
  "error": "Missing authorization header"
}
```

```json
{
  "error": "Token has expired"
}
```

```json
{
  "error": "Invalid token"
}
```

### 404 Not Found
```json
{
  "success": false,
  "error": "User not found"
}
```

```json
{
  "success": false,
  "error": "Weather subscription not found or not enabled"
}
```

### 429 Rate Limit Exceeded
```json
{
  "error": "Rate limit exceeded"
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "error": "Internal server error"
}
```

---

## Swift Integration Example

```swift
import Foundation

class DailyBriefAPI {
    let baseURL = "https://your-api-domain.com"
    let apiKey = "your_api_key"
    var jwtToken: String?
    
    // MARK: - Authentication
    
    func login(email: String, password: String, completion: @escaping (Result<String, Error>) -> Void) {
        let url = URL(string: "\(baseURL)/api/users/authenticate")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue(apiKey, forHTTPHeaderField: "X-API-Key")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = ["email": email, "password": password]
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            guard let data = data, error == nil else {
                completion(.failure(error!))
                return
            }
            
            if let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
               let token = json["token"] as? String {
                self.jwtToken = token
                completion(.success(token))
            } else {
                completion(.failure(NSError(domain: "API", code: 401)))
            }
        }.resume()
    }
    
    // MARK: - Data Fetching
    
    func getDailyBrief(completion: @escaping (Result<DailyBrief, Error>) -> Void) {
        guard let token = jwtToken else {
            completion(.failure(NSError(domain: "API", code: 401, userInfo: [NSLocalizedDescriptionKey: "Not authenticated"])))
            return
        }
        
        let url = URL(string: "\(baseURL)/api/v2/daily-brief")!
        var request = URLRequest(url: url)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            guard let data = data, error == nil else {
                completion(.failure(error!))
                return
            }
            
            do {
                let decoder = JSONDecoder()
                decoder.dateDecodingStrategy = .iso8601
                let response = try decoder.decode(DailyBriefResponse.self, from: data)
                completion(.success(response.data))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }
    
    func getWeather(completion: @escaping (Result<Weather, Error>) -> Void) {
        guard let token = jwtToken else {
            completion(.failure(NSError(domain: "API", code: 401)))
            return
        }
        
        let url = URL(string: "\(baseURL)/api/v2/weather")!
        var request = URLRequest(url: url)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            guard let data = data, error == nil else {
                completion(.failure(error!))
                return
            }
            
            do {
                let decoder = JSONDecoder()
                let response = try decoder.decode(WeatherResponse.self, from: data)
                completion(.success(response.data))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }
}

// MARK: - Models

struct DailyBriefResponse: Codable {
    let success: Bool
    let data: DailyBrief
}

struct DailyBrief: Codable {
    let user: User
    let modulesEnabled: ModulesEnabled
    let weather: Weather?
    let countdowns: [Countdown]?
    let nameday: Nameday?
    let reminders: [Reminder]?
    let generatedAt: String
    
    enum CodingKeys: String, CodingKey {
        case user, weather, countdowns, nameday, reminders
        case modulesEnabled = "modules_enabled"
        case generatedAt = "generated_at"
    }
}

struct User: Codable {
    let email: String
    let username: String
    let nickname: String?
    let timezone: String
    let language: String
    let personality: String
}

struct ModulesEnabled: Codable {
    let weather: Bool
    let countdown: Bool
    let reminder: Bool
}

struct Weather: Codable {
    let location: String
    let coordinates: Coordinates
    let timezone: String
    let today: DayWeather
    let weekForecast: [DayWeather]
    let summaryText: String
    
    enum CodingKeys: String, CodingKey {
        case location, coordinates, timezone, today
        case weekForecast = "week_forecast"
        case summaryText = "summary_text"
    }
}

struct Coordinates: Codable {
    let lat: Double
    let lon: Double
}

struct DayWeather: Codable {
    let date: String?
    let dayName: String?
    let tempMax: Double
    let tempMin: Double
    let precipitationSum: Double
    let precipitationProbability: Int
    let windSpeedMax: Double
    let condition: String
    
    enum CodingKeys: String, CodingKey {
        case date, condition
        case dayName = "day_name"
        case tempMax = "temp_max"
        case tempMin = "temp_min"
        case precipitationSum = "precipitation_sum"
        case precipitationProbability = "precipitation_probability"
        case windSpeedMax = "wind_speed_max"
    }
}

struct Countdown: Codable {
    let name: String
    let date: String
    let yearly: Bool
    let daysLeft: Int
    let nextOccurrence: String
    let isPast: Bool
    let message: String
    
    enum CodingKeys: String, CodingKey {
        case name, date, yearly, message
        case daysLeft = "days_left"
        case nextOccurrence = "next_occurrence"
        case isPast = "is_past"
    }
}

struct Nameday: Codable {
    let date: String
    let dayName: String
    let names: String
    let message: String
    let language: String
    
    enum CodingKeys: String, CodingKey {
        case date, names, message, language
        case dayName = "day_name"
    }
}

struct Reminder: Codable {
    // To be implemented
}
```

---

## Testing

Use the provided test script:
```bash
python test_jwt_api.py
```

Or use curl:
```bash
# 1. Login and get token
TOKEN=$(curl -X POST http://localhost:5001/api/users/authenticate \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  | jq -r '.token')

# 2. Get daily brief
curl http://localhost:5001/api/v2/daily-brief \
  -H "Authorization: Bearer $TOKEN"

# 3. Get weather
curl http://localhost:5001/api/v2/weather \
  -H "Authorization: Bearer $TOKEN"

# 4. Get countdowns
curl http://localhost:5001/api/v2/countdowns \
  -H "Authorization: Bearer $TOKEN"

# 5. Get nameday
curl http://localhost:5001/api/v2/nameday \
  -H "Authorization: Bearer $TOKEN"
```

---

## Rate Limits & Best Practices

1. **Token Management**:
   - Store JWT token securely in iOS Keychain
   - Token expires after 7 days - implement automatic re-login
   - Check token expiration before making requests

2. **Rate Limits**:
   - 50 requests per hour combined for all v2 endpoints
   - Implement caching in your app
   - Consider background refresh intervals (e.g., every 30 minutes for weather)

3. **Error Handling**:
   - Always check `success` field in response
   - Handle 401 errors by re-authenticating
   - Implement retry logic with exponential backoff for 5xx errors

4. **Performance**:
   - Use `/api/v2/daily-brief` for initial app load (gets all data at once)
   - Use individual endpoints for specific refreshes
   - Cache responses locally

---

## Environment Variables

Add to your `.env` file:
```env
# Existing
API_KEYS=your_api_key_here
APP_DB_PATH=app.db

# New for JWT
JWT_SECRET_KEY=your_secret_key_here_make_it_long_and_random
```

Generate secure keys:
```python
import secrets
print("API_KEY:", secrets.token_urlsafe(32))
print("JWT_SECRET_KEY:", secrets.token_urlsafe(64))
```

---

## Migration from Old API

**Old endpoints** (still available, requires API key only):
- `POST /api/users/authenticate` - Now returns JWT token
- `GET /api/weather/preview/<email>` - Returns text summary
- `GET /api/countdowns/<email>` - Basic countdown list

**New endpoints** (JWT protected, structured data):
- `GET /api/v2/daily-brief` - Complete structured data
- `GET /api/v2/weather` - Structured weather with forecast
- `GET /api/v2/countdowns` - Structured countdowns
- `GET /api/v2/nameday` - Structured nameday data

**Recommendation**: Use v2 endpoints for all new development.
