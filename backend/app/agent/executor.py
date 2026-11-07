import logging

from app.agent.tool_registry import ToolRegistry
from app.schemas import Tool, ToolCall, ToolResult
from app.tools import IMPLEMENTATIONS
from app.tools.errors import ToolError

log = logging.getLogger(__name__)


def validate_arguments(tool: Tool, args: dict) -> dict:
    """Check names and coerce types against the tool schema. Raises ToolError on a problem."""
    extra = set(args) - set(tool.parameters)
    if extra:
        raise ToolError(f"unexpected arguments: {sorted(extra)}")
    clean = {}
    for name, spec in tool.parameters.items():
        if name not in args:
            if spec.required:
                raise ToolError(f"missing argument: {name}")
            continue
        v = args[name]
        try:
            if spec.type == "number":
                v = float(v)
            elif spec.type == "integer":
                v = int(float(v))
            elif spec.type == "boolean":
                if not isinstance(v, bool):
                    raise ValueError
            else:
                v = str(v)
        except (TypeError, ValueError) as e:
            raise ToolError(f"argument {name} must be {spec.type}") from e
        clean[name] = v
    return clean


def execute(call: ToolCall, registry: ToolRegistry) -> ToolResult:
    if call.tool is None:
        return ToolResult(ok=False, error="no tool selected")
    impl = IMPLEMENTATIONS.get(call.tool)
    if impl is None:
        return ToolResult(ok=False, error=f"no implementation for {call.tool}")
    try:
        args = validate_arguments(registry.get(call.tool), call.arguments)
        return ToolResult(ok=True, output=impl(**args))
    except ToolError as e:
        return ToolResult(ok=False, error=str(e))
    except Exception:  # a tool bug must not crash the request
        log.exception("tool %s failed", call.tool)
        return ToolResult(ok=False, error="tool failed")
