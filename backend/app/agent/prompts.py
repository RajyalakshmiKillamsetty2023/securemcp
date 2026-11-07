import json

from app.schemas import Tool

PROMPT_VERSION = "sel-v1"


def build_selection_prompt(query: str, tools: list[Tool]) -> str:
    lines = []
    for t in tools:
        params = {n: p.type for n, p in t.parameters.items()}
        lines.append(f"- {t.name}: {t.description}")
        lines.append(f"  parameters: {json.dumps(params)}")
    tool_block = "\n".join(lines)
    return (
        "You are a tool-selection assistant. Choose the single best tool for the user's request.\n\n"
        f"Available tools:\n{tool_block}\n\n"
        "Rules:\n"
        "- Use only a tool from the list above.\n"
        "- Fill in the arguments from the request.\n"
        '- If no tool fits, set "tool" to null.\n'
        '- Reply with one JSON object and nothing else: {"tool": "<name or null>", "arguments": {...}}\n\n'
        f"Query: {query.strip()}\n"
        "Answer:"
    )
