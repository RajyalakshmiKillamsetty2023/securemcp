import ast
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.agent.agent import Agent
from app.agent.executor import execute, validate_arguments
from app.agent.parser import parse_tool_call
from app.agent.prompts import build_selection_prompt
from app.agent.tool_registry import ToolRegistry
from app.api.deps import get_repository
from app.api.routes_agent import get_agent
from app.llm.cache import CachedLLM, CacheMiss, JsonlCache
from app.llm.client import LLMClient
from app.llm.mock_client import MockLLMClient
from app.main import app
from app.schemas import AgentRequest, ToolCall
from app.storage.repositories import InMemoryRunRepository
from app.tools.errors import ToolError


# ---------- registry ----------
def test_registry_orders():
    given = ToolRegistry.from_catalog().names()
    assert len(given) == 10
    assert ToolRegistry.from_catalog(order="reverse").names() == given[::-1]
    a = ToolRegistry.from_catalog(order="shuffle", seed=1).names()
    assert a == ToolRegistry.from_catalog(order="shuffle", seed=1).names()
    assert sorted(a) == sorted(given)


def test_registry_n_tools():
    assert len(ToolRegistry.from_catalog(n=4).names()) == 4
    with pytest.raises(ValueError):
        ToolRegistry.from_catalog(n=11)


# ---------- parser ----------
def test_parser_variants():
    reg = ToolRegistry.from_catalog()
    ok = parse_tool_call('```json\n{"tool": "get_weather", "arguments": {"city": "Tokyo"}}\n```', reg)
    assert ok.tool == "get_weather" and ok.arguments == {"city": "Tokyo"}
    chatter = parse_tool_call('Sure! {"tool": "calculator", "arguments": {"expression": "1+1"}} done', reg)
    assert chatter.tool == "calculator"
    assert parse_tool_call('{"tool": null, "arguments": {}}', reg).parse_error is None
    assert parse_tool_call("no json here", reg).parse_error == "no_json"
    assert parse_tool_call('{"tool": "rm_rf", "arguments": {}}', reg).parse_error.startswith("unknown_tool")
    assert parse_tool_call('{"tool": "get_weather", "arguments": "x"}', reg).parse_error == "bad_arguments"


# ---------- executor ----------
def test_executor_runs_and_rejects():
    reg = ToolRegistry.from_catalog()
    r = execute(ToolCall(tool="calculator", arguments={"expression": "2 + 3 * 4"}), reg)
    assert r.ok and r.output["result"] == 14
    assert not execute(ToolCall(tool="calculator", arguments={"expression": "__import__('os')"}), reg).ok
    assert not execute(ToolCall(tool="get_weather", arguments={}), reg).ok
    assert not execute(ToolCall(tool="get_weather", arguments={"city": "X", "evil": 1}), reg).ok
    assert not execute(ToolCall(tool=None), reg).ok


def test_validate_arguments_coerces():
    tool = ToolRegistry.from_catalog().get("convert_currency")
    assert validate_arguments(tool, {"amount": "5", "from_currency": "usd", "to_currency": "eur"})["amount"] == 5.0
    with pytest.raises(ToolError):
        validate_arguments(tool, {"amount": "abc", "from_currency": "usd", "to_currency": "eur"})


# ---------- sandbox: tools must stay fake ----------
FORBIDDEN_IMPORTS = {"os", "sys", "subprocess", "socket", "requests", "httpx", "urllib", "http",
                     "pathlib", "shutil", "ftplib", "importlib", "ctypes", "pickle"}
FORBIDDEN_CALLS = {"open", "eval", "exec", "compile", "__import__", "input"}


def test_tools_are_sandboxed():
    tools_dir = Path(__file__).resolve().parent.parent / "app" / "tools"
    for path in tools_dir.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert not {a.name.split(".")[0] for a in node.names} & FORBIDDEN_IMPORTS, path.name
            if isinstance(node, ast.ImportFrom) and node.module:
                assert node.module.split(".")[0] not in FORBIDDEN_IMPORTS, path.name
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                assert node.func.id not in FORBIDDEN_CALLS, f"{path.name}: {node.func.id}"


# ---------- cache ----------
class CountingLLM(LLMClient):
    model = "counting"

    def __init__(self):
        self.calls = 0

    def complete(self, prompt, temperature=0.0):
        self.calls += 1
        return '{"tool": null, "arguments": {}}'


def test_cache_hits_and_persists(tmp_path):
    path = tmp_path / "c.jsonl"
    inner = CountingLLM()
    llm = CachedLLM(inner, JsonlCache(path))
    llm.complete("p")
    llm.complete("p")
    assert inner.calls == 1
    llm.complete("q")
    assert inner.calls == 2
    reopened = CachedLLM(CountingLLM(), JsonlCache(path))  # survives a restart
    reopened.complete("p")
    assert reopened.inner.calls == 0


def test_replay_mode_raises_on_miss(tmp_path):
    with pytest.raises(CacheMiss):
        CachedLLM(None, JsonlCache(tmp_path / "e.jsonl"), model="m").complete("nothing recorded")


# ---------- end to end with the offline mock ----------
@pytest.mark.parametrize("query,tool,key,value", [
    ("What is the weather in Hyderabad today?", "get_weather", "city", "Hyderabad"),
    ("What is 15 * 4?", "calculator", "result", 60),
    ("Convert 100 USD to INR", "convert_currency", "converted", 8300.0),
    ("Find flights from Delhi to Mumbai on 2026-12-01", "search_flights", "origin", "Delhi"),
])
def test_agent_selects_and_runs_tool(query, tool, key, value):
    resp = Agent(MockLLMClient()).run(AgentRequest(query=query))
    assert resp.call.tool == tool
    assert resp.executed and resp.result.ok
    assert resp.result.output[key] == value


def test_prompt_contains_all_tools_and_query():
    reg = ToolRegistry.from_catalog(n=3)
    p = build_selection_prompt("hello?", reg.tools)
    assert all(n in p for n in reg.names()) and "Query: hello?" in p


def test_api_run_and_errors():
    app.dependency_overrides[get_agent] = lambda: Agent(MockLLMClient())
    app.dependency_overrides[get_repository] = lambda: InMemoryRunRepository()
    try:
        c = TestClient(app)
        r = c.post("/agent/run", json={"query": "What is 2 + 2?"})
        assert r.status_code == 200 and r.json()["call"]["tool"] == "calculator"
        assert c.post("/agent/run", json={"query": ""}).status_code == 422
        assert c.post("/agent/run", json={"query": "x", "n_tools": 11}).status_code == 422
    finally:
        app.dependency_overrides.clear()
