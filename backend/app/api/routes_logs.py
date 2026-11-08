import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pymongo.errors import PyMongoError

from app.api.deps import get_repository
from app.storage.repositories import RunRepository

log = logging.getLogger(__name__)
router = APIRouter(prefix="/logs", tags=["logs"])

Repo = Annotated[RunRepository, Depends(get_repository)]


@router.get("")
def list_logs(
    repo: Repo,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    skip: Annotated[int, Query(ge=0)] = 0,
) -> dict:
    try:
        items, total = repo.list(limit=limit, skip=skip)
    except PyMongoError as e:
        log.exception("storage error")
        raise HTTPException(status_code=503, detail="storage unavailable") from e
    return {"items": items, "total": total}


@router.get("/{request_id}")
def get_log(request_id: Annotated[str, Path(pattern=r"^[A-Za-z0-9_-]{8,64}$")], repo: Repo) -> dict:
    try:
        doc = repo.get(request_id)
    except PyMongoError as e:
        log.exception("storage error")
        raise HTTPException(status_code=503, detail="storage unavailable") from e
    if doc is None:
        raise HTTPException(status_code=404, detail="run not found")
    return doc
