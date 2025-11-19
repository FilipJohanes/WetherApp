# summary_service.py
"""
Provides weather summary generation logic to avoid circular imports.
"""

def generate_weather_summary(weather, location, personality, language):
    if not weather:
        return f"Weather for {location} is unavailable."
    temp_max = weather.get('temp_max', 20)
    temp_min = weather.get('temp_min', 10)
    precipitation = weather.get('precipitation_sum', 0)
    wind_speed = weather.get('wind_speed_max', 5)
    summary = (
        f"Temperature: {temp_min}°C to {temp_max}°C. "
        f"Precipitation: {precipitation}mm. "
        f"Wind: {wind_speed}km/h. "
        f"Location: {location}. Personality: {personality}. Language: {language}."
    )
    return summary
