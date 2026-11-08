import { EventEmitter } from "node:events";

export const MAX_CLIENTS = 50;
const HEARTBEAT_MS = 25_000;

export class EventBus {
  constructor() {
    this.emitter = new EventEmitter();
    this.emitter.setMaxListeners(MAX_CLIENTS + 10);
  }
  publish(type, data) {
    this.emitter.emit("event", { type, data });
  }
  subscribe(fn) {
    this.emitter.on("event", fn);
    return () => this.emitter.off("event", fn);
  }
  get size() {
    return this.emitter.listenerCount("event");
  }
}

export function sseHandler(bus) {
  return (req, res) => {
    if (bus.size >= MAX_CLIENTS) return res.status(503).json({ error: "too many live connections" });
    res.status(200).set({
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
      "X-Accel-Buffering": "no",
    });
    res.flushHeaders();
    res.write("retry: 3000\n\n");
    const unsubscribe = bus.subscribe(({ type, data }) => {
      res.write(`event: ${type}\ndata: ${JSON.stringify(data)}\n\n`);
    });
    const heartbeat = setInterval(() => res.write(": keepalive\n\n"), HEARTBEAT_MS);
    req.on("close", () => {
      clearInterval(heartbeat);
      unsubscribe();
    });
  };
}
