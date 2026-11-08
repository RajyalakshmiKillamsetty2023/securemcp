"""Structured JSON logging with a request ID carried through each request."""
import json
import logging
import re
import sys
import uuid
from contextvars import ContextVar
from datetime import UTC, datetime

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)

_VALID_ID = re.compile(r"^[A-Za-z0-9_-]{8,64}$")


def new_request_id() -> str:
    return uuid.uuid4().hex


def accept_request_id(candidate: str | None) -> str:
    """Use the caller's ID only if it is a safe token; otherwise make a new one."""
    if candidate and _VALID_ID.fullmatch(candidate):
        return candidate
    return new_request_id()


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.fromtimestamp(record.created, UTC).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": request_id_var.get(),
        }
        fields = getattr(record, "fields", None)
        if isinstance(fields, dict):
            payload.update(fields)
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def setup_logging(level: str = "INFO") -> None:
    root = logging.getLogger()
    root.setLevel(level.upper())
    for h in list(root.handlers):
        if getattr(h, "_securemcp", False):
            root.removeHandler(h)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    handler._securemcp = True
    root.addHandler(handler)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)  # the middleware logs requests
