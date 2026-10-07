import { createApp } from "./app.js";

const port = process.env.NODE_PORT || 3001;
createApp().listen(port, "127.0.0.1", () =>
  console.log(`api-node listening on http://127.0.0.1:${port}`)
);
