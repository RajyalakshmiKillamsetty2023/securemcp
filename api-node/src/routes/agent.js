import { Router } from "express";
import { z } from "zod";

const runSchema = z.object({
  query: z.string().min(1).max(2000),
  n_tools: z.number().int().min(1).max(64).optional(),
  order: z.enum(["given", "reverse", "shuffle"]).optional(),
  seed: z.number().int().optional(),
}).strict();

export function agentRouter({ python, bus }) {
  const r = Router();
  r.post("/run", async (req, res, next) => {
    try {
      const payload = runSchema.parse(req.body);
      const run = await python.runAgent(payload, req.id);
      bus.publish("run", run);
      res.json(run);
    } catch (e) {
      next(e);
    }
  });
  return r;
}
