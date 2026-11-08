async function request(path, options = {}) {
  const res = await fetch(path, { headers: { "content-type": "application/json" }, ...options });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = data.detail ?? data.error ?? `HTTP ${res.status}`;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return data;
}

export const fetchRuns = (limit = 50) => request(`/api/logs?limit=${limit}`);

export const runAgent = (payload) =>
  request("/api/agent/run", { method: "POST", body: JSON.stringify(payload) });

// Live updates. Returns a function that closes the stream.
export function subscribeToRuns(onRun, onStatus) {
  const source = new EventSource("/api/events");
  source.onopen = () => onStatus("live");
  source.onerror = () => onStatus("reconnecting");
  source.addEventListener("run", (e) => onRun(JSON.parse(e.data)));
  return () => source.close();
}
