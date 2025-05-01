import requests

def get_weather(location="default"):
    """
    Get current weather data for the specified location
    If location is "default", returns weather for Brasov, Romania
    Otherwise expects a dict with lat/lon coordinates
    """
    try:
        # Default location: Brasov, Romania
        if location == "default":
            lat = 45.6427
            lon = 25.5887
            location_name = "Brasov, Romania"
        else:
            # For user profiles with custom locations
            lat = location["lat"]
            lon = location["lon"]
            location_name = location["name"]
        
        # Call Open-Meteo API
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code,wind_speed_10m&temperature_unit=fahrenheit"
        
        response = requests.get(url)
        data = response.json()
        
        # Extract current weather data
        temp = round(data["current"]["temperature_2m"])
        weather_code = data["current"]["weather_code"]
        wind = round(data["current"]["wind_speed_10m"])
        
        # Convert weather code to readable condition
        condition = get_weather_condition(weather_code)
        
        return {
            "temperature": temp,
            "condition": condition,
            "wind": wind,
            "location": location_name
        }
    except Exception as e:
        print(f"Error getting weather: {e}")
        # Return default values if API call fails
        return {
            "temperature": 50,
            "condition": "Unknown",
            "wind": 5,
            "location": "Brasov, Romania" if location == "default" else location.get("name", "Unknown")
        }

def get_weather_condition(code):
    """Convert weather code to readable condition"""
    # Simplified mapping of WMO weather codes
    if code == 0:
        return "Clear sky"
    elif code in [1, 2, 3]:
        return "Partly cloudy"
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

if __name__ == "__main__":
    # Test the default location
    weather = get_weather()
    print(f"Default location: {weather['location']}")
    print(f"Current weather: {weather['temperature']}°F, {weather['condition']}")
    print(f"Wind: {weather['wind']} mph")
    
    # Test a custom location (Chandler, AZ)
    chandler = {
        "lat": 33.3062,
        "lon": -111.8413,
        "name": "Chandler, AZ"
    }
    weather = get_weather(chandler)
    print(f"\nCustom location: {weather['location']}")
    print(f"Current weather: {weather['temperature']}°F, {weather['condition']}")
    print(f"Wind: {weather['wind']} mph")