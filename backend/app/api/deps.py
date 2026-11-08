from functools import lru_cache

from app.config import settings
from app.storage.mongo import get_collection
from app.storage.repositories import (
    InMemoryRunRepository,
    MongoRunRepository,
    RunRepository,
)


@lru_cache
def get_repository() -> RunRepository:
    if settings.storage_mode == "memory":
        return InMemoryRunRepository()
    return MongoRunRepository(get_collection(settings))
