from app.tools.errors import ToolError

_TO_BASE = {"km": 1000.0, "m": 1.0, "mile": 1609.34, "miles": 1609.34, "kg": 1000.0,
            "g": 1.0, "lb": 453.592, "lbs": 453.592}
_KIND = {"km": "len", "m": "len", "mile": "len", "miles": "len",
         "kg": "mass", "g": "mass", "lb": "mass", "lbs": "mass"}


def run(value: float, from_unit: str, to_unit: str) -> dict:
    a, b = from_unit.strip().lower(), to_unit.strip().lower()
    if a not in _TO_BASE or b not in _TO_BASE or _KIND[a] != _KIND[b]:
        raise ToolError("unsupported or incompatible units")
    return {"value": value, "from": a, "to": b, "converted": round(value * _TO_BASE[a] / _TO_BASE[b], 4)}
