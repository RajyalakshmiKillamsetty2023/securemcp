import hashlib
import json
import threading
from pathlib import Path

from app.llm.client import LLMClient


class CacheMiss(Exception):
    """Raised in replay mode when a prompt has no recorded response."""


def cache_key(model: str, prompt: str, temperature: float) -> str:
    payload = json.dumps([model, prompt, round(temperature, 4)], ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class JsonlCache:
    """Append-only JSONL file. Point the path at Google Drive on Colab so it survives disconnects."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._data: dict[str, str] = {}
        self._lock = threading.Lock()
        if self.path.exists():
            with open(self.path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        row = json.loads(line)
                        self._data[row["key"]] = row["response"]

    def get(self, key: str) -> str | None:
        return self._data.get(key)

    def set(self, key: str, response: str) -> None:
        with self._lock:
            self._data[key] = response
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"key": key, "response": response}, ensure_ascii=False) + "\n")

    def __len__(self) -> int:
        return len(self._data)


class CachedLLM(LLMClient):
    """Cache in front of a real client. With inner=None it is a pure replay client."""

    def __init__(self, inner: LLMClient | None, cache: JsonlCache, model: str | None = None):
        self.inner = inner
        self.cache = cache
        self.model = model or (inner.model if inner else "replay")

    def complete(self, prompt: str, temperature: float = 0.0) -> str:
        key = cache_key(self.model, prompt, temperature)
        hit = self.cache.get(key)
        if hit is not None:
            return hit
        if self.inner is None:
            raise CacheMiss("no cached response for this prompt (replay mode)")
        response = self.inner.complete(prompt, temperature)
        self.cache.set(key, response)
        return response
