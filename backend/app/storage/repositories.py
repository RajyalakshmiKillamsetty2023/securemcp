from typing import Protocol


class RunRepository(Protocol):
    def save(self, doc: dict) -> None: ...

    def list(self, limit: int = 50, skip: int = 0) -> tuple[list[dict], int]:
        """Newest first. Returns (items, total count)."""
        ...

    def get(self, request_id: str) -> dict | None: ...


class InMemoryRunRepository:
    """For tests and quick development. Data is lost when the process stops."""

    def __init__(self) -> None:
        self._docs: dict[str, dict] = {}

    def save(self, doc: dict) -> None:
        self._docs[doc["request_id"]] = dict(doc)

    def list(self, limit: int = 50, skip: int = 0) -> tuple[list[dict], int]:
        rows = sorted(self._docs.values(), key=lambda d: d["created_at"], reverse=True)
        return rows[skip: skip + limit], len(rows)

    def get(self, request_id: str) -> dict | None:
        return self._docs.get(request_id)


class MongoRunRepository:
    """Stores one document per run in a MongoDB collection, with request_id as _id."""

    def __init__(self, collection) -> None:
        self.col = collection
        self.col.create_index([("created_at", -1)])

    def save(self, doc: dict) -> None:
        self.col.insert_one({"_id": doc["request_id"], **doc})

    def list(self, limit: int = 50, skip: int = 0) -> tuple[list[dict], int]:
        cursor = self.col.find({}, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit)
        return list(cursor), self.col.count_documents({})

    def get(self, request_id: str) -> dict | None:
        return self.col.find_one({"_id": request_id}, {"_id": 0})
