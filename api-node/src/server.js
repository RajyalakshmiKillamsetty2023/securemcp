import { createApp } from "./app.js";
import { config } from "./config.js";
import { logger } from "./logger.js";

const server = createApp().listen(config.port, config.host, () =>
  logger.info({ url: `http://${config.host}:${config.port}`, python: config.pythonApiUrl }, "api-node listening")
);

for (const sig of ["SIGINT", "SIGTERM"]) {
  process.on(sig, () => server.close(() => process.exit(0)));
}
