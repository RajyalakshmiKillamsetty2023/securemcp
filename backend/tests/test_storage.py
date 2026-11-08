from datetime import UTC, datetime, timedelta

import pytest

from app.storage.repositories import InMemoryRunRepository, MongoRunRepository


def make_doc(i: int) -> dict:
    return {"request_id": f"req{i:08d}", "created_at": datetime(2026, 1, 1, tzinfo=UTC) + timedelta(minutes=i),
            "query": f"q{i}", "call": {"tool": "calculator"}}


def exercise(repo):
    for i in range(5):
        repo.save(make_doc(i))
    items, total = repo.list(limit=2)
    assert total == 5
    assert [d["query"] for d in items] == ["q4", "q3"]  # newest first
    assert [d["query"] for d in repo.list(limit=2, skip=2)[0]] == ["q2", "q1"]
    assert repo.get("req00000003")["query"] == "q3"
    assert repo.get("missing000") is None
    assert "_id" not in repo.get("req00000003")
    assert all("_id" not in d for d in items)


def test_in_memory_repository():
    exercise(InMemoryRunRepository())


def test_mongo_repository_with_mongomock():
    mongomock = pytest.importorskip("mongomock")
    exercise(MongoRunRepository(mongomock.MongoClient().db.runs))
