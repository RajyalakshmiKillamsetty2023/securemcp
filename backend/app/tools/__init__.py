"""Fake, sandboxed tools. They return canned data only: no files, network or credentials."""
from app.tools import (
    calculator,
    calendar_event,
    currency,
    db_lookup,
    flights,
    news,
    stock,
    translate,
    units,
    weather,
)

IMPLEMENTATIONS = {
    "get_weather": weather.run,
    "calculator": calculator.run,
    "search_flights": flights.run,
    "db_lookup": db_lookup.run,
    "translate_text": translate.run,
    "get_stock_price": stock.run,
    "get_news": news.run,
    "convert_currency": currency.run,
    "convert_units": units.run,
    "create_calendar_event": calendar_event.run,
}
