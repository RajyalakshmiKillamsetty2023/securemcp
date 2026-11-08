// Calls the FastAPI service. GETs retry on connection errors and 502/503/504.
// POST /agent/run retries only when no connection was made, so a run is never executed twice.

export class PythonApiError extends Error {
  constructor(status, detail) {
    super(typeof detail === "string" ? detail : JSON.stringify(detail));
    this.status = status;
    this.detail = detail;
  }
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const RETRYABLE_STATUS = new Set([502, 503, 504]);

export function createPythonClient({ baseUrl, timeoutMs = 120_000, retries = 2, backoffMs = 200 }) {
  async function request(method, path, { body, requestId } = {}) {
    const idempotent = method === "GET";
    let lastError;
    for (let attempt = 0; attempt <= retries; attempt++) {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), timeoutMs);
      try {
        const res = await fetch(`${baseUrl}${path}`, {
          method,
          headers: {
            "content-type": "application/json",
            ...(requestId ? { "x-request-id": requestId } : {}),
          },
          body: body === undefined ? undefined : JSON.stringify(body),
          signal: controller.signal,
        });
        const data = await res.json().catch(() => ({}));
        if (res.ok) return data;
        const err = new PythonApiError(res.status, data.detail ?? "agent service error");
        if (idempotent && RETRYABLE_STATUS.has(res.status) && attempt < retries) {
          lastError = err;
          await sleep(backoffMs * (attempt + 1));
          continue;
        }
        throw err;
      } catch (e) {
        if (e instanceof PythonApiError) throw e;
        if (e.name === "AbortError") throw new PythonApiError(504, "agent service timed out");
        lastError = new PythonApiError(502, "agent service unavailable"); // no connection made
        if (attempt < retries) {
          await sleep(backoffMs * (attempt + 1));
          continue;
        }
      } finally {
        clearTimeout(timer);
      }
    }
    throw lastError;
  }

  return {
    runAgent: (payload, requestId) => request("POST", "/agent/run", { body: payload, requestId }),
    listLogs: (query, requestId) => request("GET", `/logs?${new URLSearchParams(query)}`, { requestId }),
    getLog: (id, requestId) => request("GET", `/logs/${encodeURIComponent(id)}`, { requestId }),
  };
}
