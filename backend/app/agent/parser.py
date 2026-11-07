import json
import re

from app.agent.tool_registry import ToolRegistry
from app.schemas import ToolCall

_NONE_NAMES = {"", "null", "none"}


def _extract_json(raw: str) -> dict | None:
    """First JSON object containing a "tool" key; tolerates code fences and extra chatter."""
    decoder = json.JSONDecoder()
    for m in re.finditer(r"\{", raw):
        try:
            obj, _ = decoder.raw_decode(raw[m.start():])
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and "tool" in obj:
            return obj
    return None


def parse_tool_call(raw: str, registry: ToolRegistry) -> ToolCall:
    obj = _extract_json(raw)
    if obj is None:
        return ToolCall(tool=None, raw_output=raw, parse_error="no_json")
    tool, args = obj.get("tool"), obj.get("arguments", {})
    if tool is None or (isinstance(tool, str) and tool.strip().lower() in _NONE_NAMES):
        return ToolCall(tool=None, raw_output=raw)  # the model chose no tool: not an error
    if not isinstance(tool, str) or not registry.has(tool):
        return ToolCall(tool=None, raw_output=raw, parse_error=f"unknown_tool: {tool}")
    if not isinstance(args, dict):
        return ToolCall(tool=None, raw_output=raw, parse_error="bad_arguments")
    return ToolCall(tool=tool, arguments=args, raw_output=raw)
