from typing import Any, Literal

from pydantic import BaseModel, Field


class ToolParam(BaseModel):
    type: Literal["string", "number", "integer", "boolean"] = "string"
    description: str = ""
    required: bool = True


class Tool(BaseModel):
    name: str = Field(pattern=r"^[A-Za-z_][A-Za-z0-9_]*$")
    description: str
    parameters: dict[str, ToolParam] = {}
    group: str | None = None  # near-duplicate group, used by the similarity factor in E5


class AgentRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    n_tools: int | None = Field(default=None, ge=1, le=64)
    order: Literal["given", "reverse", "shuffle"] = "given"
    seed: int = 0


class ToolCall(BaseModel):
    tool: str | None
    arguments: dict[str, Any] = {}
    raw_output: str = ""
    parse_error: str | None = None


class ToolResult(BaseModel):
    ok: bool
    output: dict[str, Any] | None = None
    error: str | None = None


class GatewayDecision(BaseModel):
    decision: Literal["ALLOW", "FLAG", "BLOCK"]
    reason: str
    scores: dict[str, float] = {}


class AgentRunResponse(BaseModel):
    request_id: str
    query: str
    model: str
    prompt_version: str
    tools_offered: list[str]
    call: ToolCall
    executed: bool
    result: ToolResult | None = None
    gateway: GatewayDecision | None = None  # filled from Phase 5
    latency_ms: float
