import logging
from functools import lru_cache
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException

from app.agent.agent import Agent
from app.api.deps import get_repository
from app.config import settings
from app.llm.cache import CacheMiss
from app.llm.factory import build_llm
from app.schemas import AgentRequest, AgentRunResponse
from app.storage.repositories import RunRepository
from app.telemetry.logging import request_id_var

log = logging.getLogger(__name__)
router = APIRouter(prefix="/agent", tags=["agent"])


@lru_cache
def get_agent() -> Agent:
    return Agent(build_llm(settings))


@router.post("/run", response_model=AgentRunResponse)
def run_agent(
    req: AgentRequest,
    agent: Annotated[Agent, Depends(get_agent)],
    repo: Annotated[RunRepository, Depends(get_repository)],
) -> AgentRunResponse:
    try:
        resp = agent.run(req, request_id=request_id_var.get())
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except (httpx.HTTPError, CacheMiss) as e:
        raise HTTPException(status_code=502, detail=f"LLM unavailable: {e}") from e

    # A failure to log must not break the agent call; the response says whether it was saved.
    doc = resp.model_dump(exclude={"logged"})
    doc["request"] = req.model_dump(exclude={"query"})
    try:
        repo.save(doc)
        resp.logged = True
    except Exception:
        log.exception("could not save run")
    log.info("agent run", extra={"fields": {
        "tool": resp.call.tool, "executed": resp.executed, "logged": resp.logged,
        "latency_ms": resp.latency_ms, "model": resp.model}})
    return resp
