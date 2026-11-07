from app.tools.errors import ToolError

_PRICES = {"ACME": 101.5, "GLOBX": 54.2, "INIT": 12.75}


def run(ticker: str) -> dict:
    price = _PRICES.get(ticker.strip().upper())
    if price is None:
        raise ToolError(f"unknown ticker: {ticker}")
    return {"ticker": ticker.upper(), "price": price, "currency": "USD"}
