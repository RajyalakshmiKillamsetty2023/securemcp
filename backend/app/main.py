import logging
import time

from fastapi import FastAPI, Request

from app.api.routes_agent import router as agent_router
from app.api.routes_logs import router as logs_router
from app.config import settings
from app.telemetry.logging import accept_request_id, request_id_var, setup_logging

setup_logging(settings.log_level)
log = logging.getLogger("securemcp.http")

app = FastAPI(title="SecureMCP")
app.include_router(agent_router)
app.include_router(logs_router)


@app.middleware("http")
async def request_context(request: Request, call_next):
    rid = accept_request_id(request.headers.get("x-request-id"))
    token = request_id_var.set(rid)
    start = time.perf_counter()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        response.headers["X-Request-ID"] = rid
        return response
    finally:
        log.info("request", extra={"fields": {
            "method": request.method, "path": request.url.path, "status": status,
            "ms": round((time.perf_counter() - start) * 1000, 2)}})
        request_id_var.reset(token)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
