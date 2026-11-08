import { randomUUID } from "node:crypto";
import { logger } from "../logger.js";

export function requestContext(req, res, next) {
  req.id = randomUUID().replaceAll("-", "");
  res.set("X-Request-ID", req.id);
  const start = process.hrtime.bigint();
  res.on("finish", () => {
    logger.info({
      request_id: req.id,
      method: req.method,
      path: req.originalUrl.split("?")[0],
      status: res.statusCode,
      ms: Number(process.hrtime.bigint() - start) / 1e6,
    }, "request");
  });
  next();
}
