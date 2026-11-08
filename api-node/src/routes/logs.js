import { Router } from "express";
import { z } from "zod";

const listSchema = z.object({
  limit: z.coerce.number().int().min(1).max(200).default(50),
  skip: z.coerce.number().int().min(0).default(0),
});
const idSchema = z.string().regex(/^[A-Za-z0-9_-]{8,64}$/);

export function logsRouter({ python }) {
  const r = Router();
  r.get("/", async (req, res, next) => {
    try {
      const q = listSchema.parse(req.query);
      res.json(await python.listLogs(q, req.id));
    } catch (e) {
      next(e);
    }
  });
  r.get("/:id", async (req, res, next) => {
    try {
      res.json(await python.getLog(idSchema.parse(req.params.id), req.id));
    } catch (e) {
      next(e);
    }
  });
  return r;
}
