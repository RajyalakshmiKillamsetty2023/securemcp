import express from "express";
import helmet from "helmet";
import rateLimit from "express-rate-limit";
import { config } from "./config.js";
import { createPythonClient } from "./services/pythonClient.js";
import { EventBus, sseHandler } from "./sse.js";
import { requestContext } from "./middleware/requestId.js";
import { errorHandler, notFound } from "./middleware/errors.js";
import { agentRouter } from "./routes/agent.js";
import { logsRouter } from "./routes/logs.js";

export function createApp({
  python = createPythonClient({ baseUrl: config.pythonApiUrl, timeoutMs: config.pythonTimeoutMs }),
  bus = new EventBus(),
  rateLimitPerMinute = 120,
} = {}) {
  const app = express();
  app.disable("x-powered-by");
  app.use(helmet());
  app.use(requestContext);
  app.use(express.json({ limit: "100kb" }));
  app.use(rateLimit({ windowMs: 60_000, limit: rateLimitPerMinute }));

  app.get("/health", (_req, res) => res.json({ status: "ok" }));
  app.get("/api/events", sseHandler(bus));
  app.use("/api/agent", agentRouter({ python, bus }));
  app.use("/api/logs", logsRouter({ python }));

  app.use(notFound);
  app.use(errorHandler);
  return app;
}
