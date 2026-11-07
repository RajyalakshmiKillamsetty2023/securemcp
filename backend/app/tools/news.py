_HEADLINES = {
    "technology": ["Chipmaker announces new low-power processor", "Open-source toolkit hits 1.0"],
    "sports": ["Local team wins regional final", "Marathon sees record entries"],
}


def run(topic: str) -> dict:
    items = _HEADLINES.get(topic.strip().lower(), ["No recent headlines for this topic"])
    return {"topic": topic, "headlines": items}
