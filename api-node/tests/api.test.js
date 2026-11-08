import { test } from "node:test";
import assert from "node:assert";
import http from "node:http";
import { createApp } from "../src/app.js";
import { createPythonClient } from "../src/services/pythonClient.js";
import { EventBus } from "../src/sse.js";

const RUN = {
  request_id: "req00000001",
  created_at: "2026-11-08T10:00:00Z",
  query: "What is 15 * 4?",
  call: { tool: "calculator", arguments: { expression: "15 * 4" } },
  executed: true,
  result: { ok: true, output: { result: 60 } },
  logged: true,
};

function listen(server) {
  return new Promise((resolve) => server.listen(0, "127.0.0.1", () => resolve(server.address().port)));
}
function stop(server) {
  server.closeAllConnections?.();
  return new Promise((resolve) => server.close(resolve));
}

// A stand-in for the FastAPI service. `behavior` can be changed per test.
async function startStub(behavior = {}) {
  const stub = { calls: [], behavior };
  const server = http.createServer((req, res) => {
    let body = "";
    req.on("data", (c) => (body += c));
    req.on("end", () => {
      stub.calls.push({ method: req.method, url: req.url, headers: req.headers, body: body ? JSON.parse(body) : null });
      const b = stub.behavior;
      if (b.hang) return; // never answers
      const status = typeof b.status === "function" ? b.status(stub.calls.length) : b.status || 200;
      res.writeHead(status, { "content-type": "application/json" });
      if (status !== 200) return res.end(JSON.stringify({ detail: b.detail || "stub error" }));
      if (req.url.startsWith("/agent/run")) return res.end(JSON.stringify({ ...RUN, request_id: req.headers["x-request-id"] }));
      if (req.url.startsWith("/logs?")) return res.end(JSON.stringify({ items: [RUN], total: 1 }));
      res.end(JSON.stringify(RUN));
    });
  });
  stub.port = await listen(server);
  stub.stop = () => stop(server);
  return stub;
}

async function startNode(stubPort, { timeoutMs = 2000, retries = 1, rateLimitPerMinute = 1000, bus = new EventBus() } = {}) {
  const python = createPythonClient({ baseUrl: `http://127.0.0.1:${stubPort}`, timeoutMs, retries, backoffMs: 5 });
  const server = createApp({ python, bus, rateLimitPerMinute }).listen(0, "127.0.0.1");
  const port = await new Promise((resolve) => server.on("listening", () => resolve(server.address().port)));
  return { base: `http://127.0.0.1:${port}`, stop: () => stop(server) };
}

const post = (base, path, body) =>
  fetch(`${base}${path}`, { method: "POST", headers: { "content-type": "application/json" }, body: typeof body === "string" ? body : JSON.stringify(body) });

test("health and unknown route", async () => {
  const stub = await startStub();
  const node = await startNode(stub.port);
  assert.deepStrictEqual(await (await fetch(`${node.base}/health`)).json(), { status: "ok" });
  assert.strictEqual((await fetch(`${node.base}/nope`)).status, 404);
  await node.stop(); await stub.stop();
});

test("run is forwarded with the same request id", async () => {
  const stub = await startStub();
  const node = await startNode(stub.port);
  const res = await post(node.base, "/api/agent/run", { query: "What is 15 * 4?", order: "reverse", seed: 2 });
  const body = await res.json();
  assert.strictEqual(res.status, 200);
  assert.strictEqual(body.call.tool, "calculator");
  assert.strictEqual(stub.calls.length, 1);
  assert.deepStrictEqual(stub.calls[0].body, { query: "What is 15 * 4?", order: "reverse", seed: 2 });
  assert.strictEqual(stub.calls[0].headers["x-request-id"], res.headers.get("x-request-id"));
  assert.strictEqual(body.request_id, res.headers.get("x-request-id"));
  await node.stop(); await stub.stop();
});

test("invalid input is rejected before reaching Python", async () => {
  const stub = await startStub();
  const node = await startNode(stub.port);
  for (const bad of [{ query: "" }, { query: "x", extra: 1 }, { query: "x", n_tools: 100 }, { query: "x", order: "random" }, {}]) {
    assert.strictEqual((await post(node.base, "/api/agent/run", bad)).status, 400, JSON.stringify(bad));
  }
  assert.strictEqual((await post(node.base, "/api/agent/run", "{not json")).status, 400);
  assert.strictEqual(stub.calls.length, 0);
  await node.stop(); await stub.stop();
});

test("Python errors are passed through; POST is never retried on a response", async () => {
  const stub = await startStub({ status: 422, detail: "n_tools=11 exceeds catalog size 10" });
  const node = await startNode(stub.port);
  const res = await post(node.base, "/api/agent/run", { query: "x" });
  assert.strictEqual(res.status, 422);
  assert.match(JSON.stringify(await res.json()), /exceeds catalog/);
  stub.behavior.status = 502;
  stub.calls.length = 0;
  assert.strictEqual((await post(node.base, "/api/agent/run", { query: "x" })).status, 502);
  assert.strictEqual(stub.calls.length, 1); // a run must never execute twice
  await node.stop(); await stub.stop();
});

test("GET retries on 502 then succeeds", async () => {
  const stub = await startStub({ status: (n) => (n === 1 ? 502 : 200) });
  const node = await startNode(stub.port);
  const res = await fetch(`${node.base}/api/logs?limit=5`);
  assert.strictEqual(res.status, 200);
  assert.strictEqual(stub.calls.length, 2);
  assert.match(stub.calls[0].url, /limit=5&skip=0/);
  await node.stop(); await stub.stop();
});

test("agent service down gives 502, slow service gives 504", async () => {
  const dead = await startStub();
  const deadPort = dead.port;
  await dead.stop();
  const node = await startNode(deadPort, { retries: 1 });
  assert.strictEqual((await post(node.base, "/api/agent/run", { query: "x" })).status, 502);
  await node.stop();

  const slow = await startStub({ hang: true });
  const node2 = await startNode(slow.port, { timeoutMs: 100, retries: 0 });
  assert.strictEqual((await post(node2.base, "/api/agent/run", { query: "x" })).status, 504);
  await node2.stop(); await slow.stop();
});

test("log detail validates the id and proxies 404", async () => {
  const stub = await startStub();
  const node = await startNode(stub.port);
  assert.strictEqual((await fetch(`${node.base}/api/logs/short`)).status, 400);
  assert.strictEqual((await fetch(`${node.base}/api/logs/req00000001`)).status, 200);
  stub.behavior.status = 404;
  stub.behavior.detail = "run not found";
  assert.strictEqual((await fetch(`${node.base}/api/logs/req00000002`)).status, 404);
  assert.strictEqual((await fetch(`${node.base}/api/logs?limit=0`)).status, 400);
  await node.stop(); await stub.stop();
});

test("a finished run is pushed to live subscribers", async () => {
  const stub = await startStub();
  const node = await startNode(stub.port);
  const controller = new AbortController();
  try {
    const stream = await fetch(`${node.base}/api/events`, { signal: controller.signal });
    assert.match(stream.headers.get("content-type"), /^text\/event-stream/);
    const reader = stream.body.getReader();
    const decoder = new TextDecoder();
    let text = decoder.decode((await reader.read()).value);
    assert.match(text, /retry: 3000/);

    await post(node.base, "/api/agent/run", { query: "What is 15 * 4?" });
    const deadline = Date.now() + 2000;
    while (!text.includes("event: run") && Date.now() < deadline) {
      text += decoder.decode((await reader.read()).value);
    }
    assert.match(text, /event: run/);
    const data = JSON.parse(text.split("data: ")[1].split("\n")[0]);
    assert.strictEqual(data.call.tool, "calculator");
  } finally {
    controller.abort();
    await node.stop();
    await stub.stop();
  }
});

test("rate limit returns 429", async () => {
  const stub = await startStub();
  const node = await startNode(stub.port, { rateLimitPerMinute: 3 });
  const codes = [];
  for (let i = 0; i < 4; i++) codes.push((await fetch(`${node.base}/health`)).status);
  assert.deepStrictEqual(codes, [200, 200, 200, 429]);
  await node.stop(); await stub.stop();
});
