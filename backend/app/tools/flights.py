def run(origin: str, destination: str, date: str) -> dict:
    return {
        "origin": origin, "destination": destination, "date": date,
        "flights": [
            {"flight": "SM101", "departs": "08:15", "arrives": "10:40", "price_usd": 120},
            {"flight": "SM245", "departs": "17:30", "arrives": "19:55", "price_usd": 98},
        ],
    }
