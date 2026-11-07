from app.config import Settings
from app.llm.cache import CachedLLM, JsonlCache
from app.llm.client import LLMClient
from app.llm.mock_client import MockLLMClient
from app.llm.ollama_client import OllamaClient
from app.llm.openai_compat_client import OpenAICompatClient


def build_llm(s: Settings) -> LLMClient:
    if s.llm_mode == "mock":
        return MockLLMClient()
    cache = JsonlCache(s.llm_cache_path)
    if s.llm_mode == "replay":
        return CachedLLM(None, cache, model=s.llm_model)
    if s.llm_mode == "ollama":
        return CachedLLM(OllamaClient(s.llm_model, s.ollama_url), cache)
    if s.llm_mode == "openai_compat":
        if not s.openai_compat_base_url:
            raise ValueError("OPENAI_COMPAT_BASE_URL is required for llm_mode=openai_compat")
        inner = OpenAICompatClient(s.llm_model, s.openai_compat_base_url, s.openai_compat_api_key)
        return CachedLLM(inner, cache)
    raise ValueError(f"unknown llm_mode: {s.llm_mode}")
