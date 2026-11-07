from app.tools.errors import ToolError

_TABLES = {
    "customers": {"c001": {"name": "Asha Rao", "tier": "gold"}, "c002": {"name": "Liam Ortiz", "tier": "basic"}},
    "products": {"p100": {"name": "Desk lamp", "stock": 42}, "p200": {"name": "Notebook", "stock": 310}},
}


def run(table: str, key: str) -> dict:
    rows = _TABLES.get(table.strip().lower())
    if rows is None:
        raise ToolError(f"unknown table: {table}")
    row = rows.get(key.strip().lower())
    if row is None:
        raise ToolError(f"no record {key} in {table}")
    return {"table": table, "key": key, "record": row}
