"""Run a few queries through the agent using the LLM mode from settings (.env).

Laptop:  python scripts/smoke_agent.py          (LLM_MODE=mock)
Colab:   set LLM_MODE=ollama, LLM_CACHE_PATH on Drive, run again, then run a second time to
         confirm the answers now come from the cache.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.agent.agent import Agent
from app.config import settings
from app.llm.factory import build_llm
from app.schemas import AgentRequest

QUERIES = [
    "What is the weather in Hyderabad today?",
    "What is 15 * 4?",
    "Convert 100 USD to INR",
    "Find flights from Delhi to Mumbai on 2026-12-01",
]

if __name__ == "__main__":
    agent = Agent(build_llm(settings))
    print(f"mode={settings.llm_mode} model={agent.llm.model}")
    for q in QUERIES:
        r = agent.run(AgentRequest(query=q))
        print(f"\nQ: {q}\n  tool={r.call.tool} args={r.call.arguments} "
              f"parse_error={r.call.parse_error}\n  result={r.result.output if r.result else None} "
              f"({r.latency_ms} ms)")
