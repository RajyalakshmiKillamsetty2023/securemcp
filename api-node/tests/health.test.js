import { test } from "node:test";
import assert from "node:assert";
import { createApp } from "../src/app.js";

test("GET /health", async () => {
  const server = createApp().listen(0);
  const { port } = server.address();
  const res = await fetch(`http://127.0.0.1:${port}/health`);
  assert.strictEqual(res.status, 200);
  assert.deepStrictEqual(await res.json(), { status: "ok" });
  server.close();
});
