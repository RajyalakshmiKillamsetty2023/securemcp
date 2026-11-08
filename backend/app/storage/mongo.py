from pymongo import MongoClient
from pymongo.collection import Collection

from app.config import Settings

RUNS_COLLECTION = "runs"


def get_collection(s: Settings) -> Collection:
    """Lazy connection: the API starts even if MongoDB is down, and saves fail with a logged error."""
    client = MongoClient(s.mongo_uri, serverSelectionTimeoutMS=2000, tz_aware=True)
    return client[s.mongo_db][RUNS_COLLECTION]
