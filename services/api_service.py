"""
API Service Module
Provides structured data formatting for API responses.
Transforms email-ready data into JSON structures for mobile apps.
"""
import os
import sqlite3
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Dict, List, Optional, Any
import requests

from services.weather_service import get_weather_forecast, generate_weather_summary
from services.countdown_service import get_user_countdowns, CountdownEvent
from services.namedays_service import get_nameday_message


def get_week_weather_forecast(lat: float, lon: float, timezone: str) -> Optional[List[Dict[str, Any]]]:
    """
    Fetch 7-day weather forecast from Open-Meteo API.
    Returns list of daily forecast dictionaries.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,windspeed_10m_max",
        "timezone": timezone,
        "forecast_days": 7
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        daily = data.get("daily", {})
        
        dates = daily.get("time", [])
        temp_max_list = daily.get("temperature_2m_max", [])
        temp_min_list = daily.get("temperature_2m_min", [])
        precip_list = daily.get("precipitation_sum", [])
        precip_prob_list = daily.get("precipitation_probability_max", [])
        wind_list = daily.get("windspeed_10m_max", [])
        
        forecast = []
        for i in range(len(dates)):
            date_str = dates[i]
            date_obj = datetime.fromisoformat(date_str)
            
            temp_max = temp_max_list[i] if i < len(temp_max_list) else None
            temp_min = temp_min_list[i] if i < len(temp_min_list) else None
            precipitation = precip_list[i] if i < len(precip_list) else 0
            precip_prob = precip_prob_list[i] if i < len(precip_prob_list) else 0
            wind_speed = wind_list[i] if i < len(wind_list) else 0
            
            # Determine condition based on weather data
            condition = _determine_weather_condition(
                temp_max or 20, 
                temp_min or 10, 
                precipitation or 0, 
                wind_speed or 0, 
                precip_prob or 0
            )
            
            forecast.append({
                "date": date_str,
                "day_name": date_obj.strftime("%A"),
                "temp_max": round(temp_max, 1) if temp_max is not None else None,
                "temp_min": round(temp_min, 1) if temp_min is not None else None,
                "precipitation_sum": round(precipitation, 1) if precipitation is not None else 0,
                "precipitation_probability": int(precip_prob) if precip_prob is not None else 0,
                "wind_speed_max": round(wind_speed, 1) if wind_speed is not None else 0,
                "condition": condition
            })
        
        return forecast
    except Exception as e:
        print(f"Week forecast API error for ({lat}, {lon}): {e}")
        return None


def _determine_weather_condition(temp_max: float, temp_min: float, precipitation: float, 
                                  wind_speed: float, rain_prob: int) -> str:
    """Determine weather condition code based on weather parameters."""
    # Combined conditions
    if temp_max >= 30 and rain_prob < 20:
        return 'sunny_hot'
    if temp_max <= 5 and wind_speed >= 15:
        return 'cold_windy'
    if temp_max <= 5 and precipitation >= 2:
        return 'rainy_cold'
    # Extreme conditions
    if temp_max >= 36:
        return 'heatwave'
    if temp_min <= -15:
        return 'blizzard'
    # Thunderstorm
    if precipitation >= 10 and rain_prob >= 70:
        return 'thunderstorm'
    # Heavy rain
    if precipitation >= 7:
        return 'heavy_rain'
    # Raining
    if precipitation >= 2:
        return 'raining'
    # Snowing
    if temp_max <= 2 and precipitation > 0.5:
        return 'snowing'
    # Freezing
    if temp_min < 0 and precipitation <= 0.1:
        return 'freezing'
    # Hot
    if temp_max >= 30:
        return 'hot'
    # Cold
    if temp_max <= 5:
        return 'cold'
    # Windy
    if wind_speed >= 15:
        return 'windy'
    # Foggy
    if temp_min >= -2 and temp_max <= 8 and precipitation < 0.2 and wind_speed < 8 and rain_prob >= 60:
        return 'foggy'
    # Humid
    if rain_prob >= 70 and precipitation < 0.2:
        return 'humid'
    # Dry
    if precipitation < 0.05 and temp_max >= 25:
        return 'dry'
    # Sunny
    if temp_max >= 20 and rain_prob < 20 and precipitation < 0.1:
        return 'sunny'
    # Mild
    if temp_max >= 10 and rain_prob < 40 and precipitation < 0.2:
        return 'mild'
    # Cloudy
    if rain_prob >= 30 or precipitation > 0.05:
        return 'cloudy'
    # Fallback
    return 'default'


def get_structured_weather_data(email: str, db_path: str = None) -> Optional[Dict[str, Any]]:
    """
    Get structured weather data for a user including today's weather and week forecast.
    
    Returns:
        Dictionary with weather data or None if user has no weather subscription
    """
    if db_path is None:
        db_path = os.getenv("APP_DB_PATH", "app.db")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    try:
        # Get user's weather subscription
        subscriber = conn.execute("""
            SELECT ws.email, ws.location, ws.lat, ws.lon, 
                   COALESCE(u.timezone, 'UTC') as timezone, 
                   ws.personality, ws.language 
            FROM weather_subscriptions ws
            JOIN users u ON ws.email = u.email
            WHERE ws.email = ? AND u.weather_enabled = 1
        """, (email,)).fetchone()
        
        if not subscriber:
            return None
        
        lat = subscriber['lat']
        lon = subscriber['lon']
        timezone = subscriber['timezone']
        location = subscriber['location']
        personality = subscriber['personality']
        language = subscriber['language']
        
        # Get today's weather
        today_weather = get_weather_forecast(lat, lon, timezone)
        
        if not today_weather:
            return None
        
        # Generate summary text
        summary_text = generate_weather_summary(today_weather, location, personality, language)
        
        # Get week forecast
        week_forecast = get_week_weather_forecast(lat, lon, timezone)
        
        # Calculate rain probability for today
        precipitation = today_weather.get('precipitation_sum', 0)
        rain_prob = min(int((precipitation / 1.5) * 100), 100) if precipitation else 0
        
        # Determine today's condition
        condition = _determine_weather_condition(
            today_weather.get('temp_max', 20),
            today_weather.get('temp_min', 10),
            precipitation,
            today_weather.get('wind_speed_max', 0),
            rain_prob
        )
        
        return {
            "location": location,
            "coordinates": {
                "lat": lat,
                "lon": lon
            },
            "timezone": timezone,
            "today": {
                "temp_max": round(today_weather.get('temp_max', 0), 1),
                "temp_min": round(today_weather.get('temp_min', 0), 1),
                "precipitation_sum": round(today_weather.get('precipitation_sum', 0), 1),
                "precipitation_probability": rain_prob,
                "wind_speed_max": round(today_weather.get('wind_speed_max', 0), 1),
                "condition": condition
            },
            "week_forecast": week_forecast or [],
            "summary_text": summary_text
        }
    finally:
        conn.close()


def get_structured_countdown_data(email: str, timezone: str = 'UTC', db_path: str = None) -> List[Dict[str, Any]]:
    """
    Get structured countdown data for a user.
    
    Returns:
        List of countdown dictionaries with calculated days remaining
    """
    if db_path is None:
        db_path = os.getenv("APP_DB_PATH", "app.db")
    
    # Get user countdowns
    events = get_user_countdowns(email, db_path)
    
    if not events:
        return []
    
    # Get current time in user's timezone
    now = datetime.now(ZoneInfo(timezone))
    
    countdowns = []
    for event in events:
        event_date = event.get_next_event_date(now)
        
        if event_date:
            days_left = (event_date - now).days
            is_past = event_date < now
            
            # Get appropriate message
            message = event.get_countdown_message(now)
            
            countdowns.append({
                "name": event.name,
                "date": event.date,
                "yearly": event.yearly,
                "days_left": days_left,
                "next_occurrence": event_date.strftime("%Y-%m-%d"),
                "is_past": is_past,
                "message": message or ""
            })
    
    return countdowns


def get_structured_nameday_data(language: str = 'en', date: datetime = None) -> Optional[Dict[str, Any]]:
    """
    Get structured nameday data for a specific date and language.
    
    Returns:
        Dictionary with nameday info or None if language doesn't support namedays
    """
    if date is None:
        date = datetime.now()
    
    # Get nameday message
    message = get_nameday_message(language, date)
    
    if not message:
        return None
    
    # Extract names from message (after the prefix)
    # Message format: "Prefix: Name1, Name2"
    names = ""
    if ":" in message:
        names = message.split(":", 1)[1].strip()
    
    return {
        "date": date.strftime("%Y-%m-%d"),
        "day_name": date.strftime("%A"),
        "names": names,
        "message": message,
        "language": language
    }


def get_daily_brief_data(email: str, db_path: str = None) -> Dict[str, Any]:
    """
    Get complete daily brief data for a user in structured JSON format.
    
    Returns:
        Dictionary with all user's daily brief data (weather, countdowns, namedays, etc.)
    """
    if db_path is None:
        db_path = os.getenv("APP_DB_PATH", "app.db")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    try:
        # Get user info
        user = conn.execute("""
            SELECT email, username, nickname, timezone, 
                   weather_enabled, countdown_enabled, reminder_enabled
            FROM users
            WHERE email = ?
        """, (email,)).fetchone()
        
        if not user:
            return {"error": "User not found"}
        
        timezone = user['timezone'] or 'UTC'
        
        # Get language and personality from weather subscription if exists
        weather_sub = conn.execute("""
            SELECT language, personality FROM weather_subscriptions WHERE email = ?
        """, (email,)).fetchone()
        
        language = weather_sub['language'] if weather_sub else 'en'
        personality = weather_sub['personality'] if weather_sub else 'neutral'
        
        # Get current time in user's timezone
        user_now = datetime.now(ZoneInfo(timezone))
        
        # Build response
        response = {
            "user": {
                "email": user['email'],
                "username": user['username'],
                "nickname": user['nickname'],
                "timezone": timezone,
                "language": language,
                "personality": personality
            },
            "modules_enabled": {
                "weather": bool(user['weather_enabled']),
                "countdown": bool(user['countdown_enabled']),
                "reminder": bool(user['reminder_enabled'])
            },
            "generated_at": user_now.isoformat()
        }
        
        # Add weather data if enabled
        if user['weather_enabled']:
            weather_data = get_structured_weather_data(email, db_path)
            response['weather'] = weather_data
        
        # Add countdown data if enabled
        if user['countdown_enabled']:
            countdown_data = get_structured_countdown_data(email, timezone, db_path)
            response['countdowns'] = countdown_data
        
        # Add nameday data
        nameday_data = get_structured_nameday_data(language, user_now)
        response['nameday'] = nameday_data
        
        # Reminder placeholder (not implemented yet)
        if user['reminder_enabled']:
            response['reminders'] = []
        
        return response
        
    finally:
        conn.close()
