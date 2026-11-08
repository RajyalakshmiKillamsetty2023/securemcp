export const config = {
  port: Number(process.env.NODE_PORT) || 3001,
  host: "127.0.0.1",
  pythonApiUrl: (process.env.PYTHON_API_URL || "http://127.0.0.1:8000").replace(/\/$/, ""),
  pythonTimeoutMs: Number(process.env.PYTHON_TIMEOUT_MS) || 120_000,
  logLevel: process.env.LOG_LEVEL || "info",
};
