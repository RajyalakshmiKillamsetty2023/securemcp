from functools import lru_cache
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException

from app.agent.agent import Agent
from app.config import settings
from app.llm.cache import CacheMiss
from app.llm.factory import build_llm
from app.schemas import AgentRequest, AgentRunResponse

router = APIRouter(prefix="/agent", tags=["agent"])


@lru_cache
def get_agent() -> Agent:
    return Agent(build_llm(settings))


@router.post("/run", response_model=AgentRunResponse)
def run_agent(req: AgentRequest, agent: Annotated[Agent, Depends(get_agent)]) -> AgentRunResponse:
    try:
        return agent.run(req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except (httpx.HTTPError, CacheMiss) as e:
        raise HTTPException(status_code=502, detail=f"LLM unavailable: {e}") from e
