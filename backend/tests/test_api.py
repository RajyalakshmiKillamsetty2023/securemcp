import json
import logging

import pytest
from fastapi.testclient import TestClient

from app.agent.agent import Agent
from app.api.deps import get_repository
from app.api.routes_agent import get_agent
from app.llm.mock_client import MockLLMClient
from app.main import app
from app.storage.repositories import InMemoryRunRepository
from app.telemetry.logging import JsonFormatter, accept_request_id, request_id_var


@pytest.fixture
def client():
    repo = InMemoryRunRepository()
    app.dependency_overrides[get_agent] = lambda: Agent(MockLLMClient())
    app.dependency_overrides[get_repository] = lambda: repo
    yield TestClient(app), repo
    app.dependency_overrides.clear()


def test_run_is_saved_and_listed(client):
    c, _ = client
    r = c.post("/agent/run", json={"query": "What is 15 * 4?", "order": "reverse", "seed": 3})
    body = r.json()
    assert r.status_code == 200 and body["logged"] is True and body["call"]["tool"] == "calculator"
    listing = c.get("/logs").json()
    assert listing["total"] == 1 and listing["items"][0]["request_id"] == body["request_id"]
    detail = c.get(f"/logs/{body['request_id']}").json()
    assert detail["result"]["output"]["result"] == 60
    assert detail["request"] == {"n_tools": None, "order": "reverse", "seed": 3}
    assert "logged" not in detail


def test_request_id_flows_through(client):
    c, _ = client
    r = c.post("/agent/run", json={"query": "What is 2 + 2?"}, headers={"X-Request-ID": "abc12345-xyz"})
    assert r.headers["x-request-id"] == "abc12345-xyz"
    assert r.json()["request_id"] == "abc12345-xyz"
    bad = c.post("/agent/run", json={"query": "What is 2 + 2?"}, headers={"X-Request-ID": "bad id\nx"})
    assert bad.headers["x-request-id"] != "bad id\nx"


def test_logs_errors(client):
    c, _ = client
    assert c.get("/logs/doesnotexist1").status_code == 404
    assert c.get("/logs/short").status_code == 422
    assert c.get("/logs?limit=0").status_code == 422
    assert c.get("/logs?limit=201").status_code == 422


def test_storage_failure_does_not_break_the_agent():
    class Broken:
        def save(self, doc):
            raise RuntimeError("db down")

    app.dependency_overrides[get_agent] = lambda: Agent(MockLLMClient())
    app.dependency_overrides[get_repository] = lambda: Broken()
    try:
        r = TestClient(app).post("/agent/run", json={"query": "What is 2 + 2?"})
        assert r.status_code == 200 and r.json()["logged"] is False
    finally:
        app.dependency_overrides.clear()


def test_json_log_format_has_request_id():
    token = request_id_var.set("rid-test-1234")
    try:
        rec = logging.LogRecord("t", logging.INFO, __file__, 1, "hello", None, None)
        rec.fields = {"tool": "calculator"}
        out = json.loads(JsonFormatter().format(rec))
    finally:
        request_id_var.reset(token)
    assert out["request_id"] == "rid-test-1234" and out["msg"] == "hello" and out["tool"] == "calculator"
    assert out["level"] == "INFO" and "ts" in out


def test_accept_request_id():
    assert accept_request_id("good-id-12345") == "good-id-12345"
    assert accept_request_id(None) != accept_request_id(None)
    assert len(accept_request_id("x")) == 32
