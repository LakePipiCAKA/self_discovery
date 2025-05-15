# /home/taran/self_discovery/src/weather/open_meteo.py
import requests


def get_weather(location="default"):
    """
    Get current weather data for the specified location.
    If location is \"default\", returns weather for Brasov, Romania.
    Otherwise expects a dict with lat/lon and optional city/state/country fields.
    """
    try:
        if location == "default":
            lat = 45.6427
            lon = 25.5887
            location_name = "Brasov, Romania"
        else:
            lat = location.get("lat", 45.6427)
            lon = location.get("lon", 25.5887)
            city = location.get("city", "")
            state = location.get("state", "")
            country = location.get("country", "")
            parts = [city, state, country]
            location_name = ", ".join([p for p in parts if p])

        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&current=temperature_2m,weather_code,wind_speed_10m"
            f"&temperature_unit=fahrenheit"
        )

        response = requests.get(url)
        data = response.json()

        temp = round(data["current"]["temperature_2m"])
        weather_code = data["current"]["weather_code"]
        wind = round(data["current"]["wind_speed_10m"])
        condition = get_weather_condition(weather_code)

        return {
            "temperature": temp,
            "condition": condition,
            "wind": wind,
            "location": location_name,
        }

    except Exception as e:
        print(f"Error getting weather: {e}")
        fallback = (
            "Brasov, Romania"
            if location == "default"
            else location.get("name", "Unknown")
        )
        return {
            "temperature": 50,
            "condition": "Unknown",
            "wind": 5,
            "location": fallback,
        }


def get_weather_condition(code):
    """Convert Open Meteo weather codes to human-readable conditions."""
    if code == 0:
        return "Clear Sky"
    elif code in [1, 2, 3]:
        return "Partly Cloudy"
    elif code in [45, 48]:
        return "Foggy"
    elif code in [51, 53, 55]:
        return "Drizzle"
    elif code in [61, 63, 65]:
        return "Rain"
    elif code in [71, 73, 75]:
        return "Snow"
    elif code in [95, 96, 99]:
        return "Thunderstorm"
    else:
        return "Unknown"
