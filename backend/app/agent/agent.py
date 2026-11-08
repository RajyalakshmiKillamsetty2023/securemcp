import time
import uuid
from datetime import UTC, datetime

from app.agent.executor import execute
from app.agent.parser import parse_tool_call
from app.agent.prompts import PROMPT_VERSION, build_selection_prompt
from app.agent.tool_registry import CATALOG_PATH, ToolRegistry
from app.llm.client import LLMClient
from app.schemas import AgentRequest, AgentRunResponse


class Agent:
    def __init__(self, llm: LLMClient, catalog_path=CATALOG_PATH):
        self.llm = llm
        self.catalog_path = catalog_path

    def run(self, req: AgentRequest, request_id: str | None = None) -> AgentRunResponse:
        t0 = time.perf_counter()
        registry = ToolRegistry.from_catalog(req.n_tools, req.order, req.seed, self.catalog_path)
        prompt = build_selection_prompt(req.query, registry.tools)
        raw = self.llm.complete(prompt, temperature=0.0)
        call = parse_tool_call(raw, registry)
        # Phase 5: the gateway decision goes here, before execution.
        result = execute(call, registry) if call.tool else None
        return AgentRunResponse(
            request_id=request_id or uuid.uuid4().hex,
            created_at=datetime.now(UTC),
            query=req.query,
            model=self.llm.model,
            prompt_version=PROMPT_VERSION,
            tools_offered=registry.names(),
            call=call,
            executed=result is not None,
            result=result,
            latency_ms=round((time.perf_counter() - t0) * 1000, 2),
        )
