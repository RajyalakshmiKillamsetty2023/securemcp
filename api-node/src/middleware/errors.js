import { ZodError } from "zod";
import { PythonApiError } from "../services/pythonClient.js";
import { logger } from "../logger.js";

export function notFound(_req, res) {
  res.status(404).json({ error: "not found" });
}

export function errorHandler(err, req, res, _next) {
  if (err instanceof ZodError) {
    return res.status(400).json({
      error: "invalid request",
      issues: err.issues.map((i) => ({ path: i.path.join("."), message: i.message })),
    });
  }
  if (err instanceof PythonApiError) {
    return res.status(err.status).json({ error: err.message, detail: err.detail });
  }
  if (err.type === "entity.parse.failed" || err.type === "entity.too.large") {
    return res.status(err.status || 400).json({ error: "invalid request body" });
  }
  logger.error({ request_id: req.id, err: err.message }, "unhandled error");
  res.status(500).json({ error: "internal error" });
}
