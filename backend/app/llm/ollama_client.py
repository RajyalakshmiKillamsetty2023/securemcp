import httpx

from app.llm.client import LLMClient


class OllamaClient(LLMClient):
    """Talks to an Ollama server (runs on Colab, not on the laptop)."""

    def __init__(self, model: str, base_url: str = "http://127.0.0.1:11434", timeout: float = 180.0):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def complete(self, prompt: str, temperature: float = 0.0) -> str:
        r = httpx.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature, "seed": 0},
            },
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()["response"]
