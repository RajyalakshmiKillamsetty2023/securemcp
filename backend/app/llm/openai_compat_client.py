import httpx

from app.llm.client import LLMClient


class OpenAICompatClient(LLMClient):
    """Any OpenAI-compatible /chat/completions endpoint. Optional fallback, not required."""

    def __init__(self, model: str, base_url: str, api_key: str = "", timeout: float = 120.0):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def complete(self, prompt: str, temperature: float = 0.0) -> str:
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        r = httpx.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
            },
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
