from app.tools.errors import ToolError

_PER_USD = {"USD": 1.0, "EUR": 0.92, "INR": 83.0, "GBP": 0.79, "JPY": 150.0}


def run(amount: float, from_currency: str, to_currency: str) -> dict:
    a, b = from_currency.strip().upper(), to_currency.strip().upper()
    if a not in _PER_USD or b not in _PER_USD:
        raise ToolError("unsupported currency")
    return {"amount": amount, "from": a, "to": b,
            "converted": round(amount / _PER_USD[a] * _PER_USD[b], 2), "note": "fixed demo rates"}
