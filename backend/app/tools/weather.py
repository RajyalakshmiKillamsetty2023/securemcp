_DATA = {
    "hyderabad": {"temp_c": 31, "condition": "partly cloudy", "forecast": "dry, light breeze"},
    "london": {"temp_c": 12, "condition": "overcast", "forecast": "light rain in the evening"},
    "tokyo": {"temp_c": 18, "condition": "clear", "forecast": "sunny, mild"},
}


def run(city: str) -> dict:
    data = _DATA.get(city.strip().lower(), {"temp_c": 22, "condition": "clear", "forecast": "stable"})
    return {"city": city, **data}
