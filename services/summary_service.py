
# summary_service.py
"""
Provides message formatting for weather, countdowns, reminders, and unified daily summary.
"""

def generate_weather_summary(weather, location, personality, language):
    import os
    import csv
    from functools import lru_cache

    if not weather:
        return f"Weather for {location} is unavailable."

    temp_max = weather.get('temp_max', 20)
    temp_min = weather.get('temp_min', 10)
    precipitation = weather.get('precipitation_sum', 0)
    wind_speed = weather.get('wind_speed_max', 5)
    rain_prob = min(int((precipitation / 1.5) * 100), 100) if precipitation else 0

    # Load weather_messages.txt (cache for performance)
    @lru_cache(maxsize=8)
    def load_weather_messages(lang):
        path = os.path.join(os.path.dirname(__file__), f'../languages/{lang}/weather_messages.txt')
        messages = {}
        if not os.path.exists(path):
            return messages
        with open(path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split('|')
                if len(parts) < 2:
                    continue
                key = parts[0]
                personalities = ['neutral', 'cute', 'brutal', 'emuska']
                msg_map = dict(zip(personalities, parts[1:]))
                messages[key] = msg_map
        return messages

    messages = load_weather_messages(language)
    def get_msg(key, personality):
        msg_map = messages.get(key, {})
        return msg_map.get(personality) or msg_map.get('neutral') or messages.get('default', {}).get(personality, '')

    # Compose message
    intro = f"Today's weather for {location}:"
    temp_line = f"🌡️ Temperature: High {temp_max}°C / Low {temp_min}°C"
    rain_line = f"🌧️ Rain probability: {rain_prob}% (≈{precipitation} mm)"
    wind_line = f"💨 Wind: up to {wind_speed} km/h"

    # Determine weather condition using only keys from weather_messages.txt
    def get_condition(temp_max, temp_min, precipitation, wind_speed, rain_prob):
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

    condition = get_condition(temp_max, temp_min, precipitation, wind_speed, rain_prob)
    condition_msg = get_msg(condition, personality)

    # Clothing suggestion logic: combine all relevant conditions
    clothing = []
    # Always include the main condition advice
    if condition != 'default':
        clothing.append(get_msg(condition, personality))
    # Add advice for temperature extremes
    if temp_max >= 36:
        clothing.append(get_msg('heatwave', personality))
    if temp_min <= -15:
        clothing.append(get_msg('blizzard', personality))
    if temp_max >= 30 and rain_prob < 20:
        clothing.append(get_msg('sunny_hot', personality))
    if temp_max <= 5 and wind_speed >= 15:
        clothing.append(get_msg('cold_windy', personality))
    if temp_max <= 5 and precipitation >= 2:
        clothing.append(get_msg('rainy_cold', personality))
    # Add advice for rain and wind
    if precipitation >= 7:
        clothing.append(get_msg('heavy_rain', personality))
    elif precipitation >= 2:
        clothing.append(get_msg('raining', personality))
    if wind_speed >= 15:
        clothing.append(get_msg('windy', personality))
    # Add advice for snow/freezing
    if temp_max <= 2 and precipitation > 0.5:
        clothing.append(get_msg('snowing', personality))
    if temp_min < 0 and precipitation <= 0.1:
        clothing.append(get_msg('freezing', personality))
    # Add advice for fog/humid/dry
    if temp_min >= -2 and temp_max <= 8 and precipitation < 0.2 and wind_speed < 8 and rain_prob >= 60:
        clothing.append(get_msg('foggy', personality))
    if rain_prob >= 70 and precipitation < 0.2:
        clothing.append(get_msg('humid', personality))
    if precipitation < 0.05 and temp_max >= 25:
        clothing.append(get_msg('dry', personality))
    # Add advice for mild if nothing else
    if not clothing:
        clothing.append(get_msg('mild', personality))
    # Remove duplicates and empty
    clothing_msg = '\n'.join(dict.fromkeys([c for c in clothing if c]))

    summary = f"{intro}\n\n{temp_line}\n{rain_line}\n{wind_line}\n\n{condition_msg}\n{clothing_msg}\n"
    return summary

def generate_countdown_summary(countdowns, language='en'):
    if not countdowns:
        return "No active countdowns."
    summary = "⏳ Countdown reminders:\n"
    for cd in countdowns:
        name = cd.get('name', 'Event')
        days = cd.get('days_left', '?')
        summary += f"• {name}: {days} days left\n"
    return summary

def generate_reminder_summary(reminders, language='en'):
    if not reminders:
        return "No active reminders."
    summary = "🔔 Reminders:\n"
    for r in reminders:
        text = r.get('text', 'Reminder')
        time = r.get('time', '')
        summary += f"• {text} {time}\n"
    return summary

def generate_daily_summary(weather=None, location=None, personality='neutral', language='en', countdowns=None, reminders=None):
    sections = []
    if weather and location:
        sections.append(generate_weather_summary(weather, location, personality, language))
    if countdowns:
        sections.append(generate_countdown_summary(countdowns, language))
    if reminders:
        sections.append(generate_reminder_summary(reminders, language))
    if not sections:
        return "No active subscriptions."
    return "\n\n".join(sections)
