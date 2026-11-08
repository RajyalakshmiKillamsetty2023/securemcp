from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Reads .env from the working directory or the repo root.
    model_config = SettingsConfigDict(env_file=(".env", "../.env"), extra="ignore")

    mongo_uri: str = "mongodb://127.0.0.1:27018"
    mongo_db: str = "securemcp"

    # mock: offline keyword picker for laptop dev and tests (never for experiments)
    # ollama / openai_compat: real model, wrapped in the response cache
    # replay: cache only, raises on a miss (offline demo)
    llm_mode: Literal["mock", "ollama", "openai_compat", "replay"] = "mock"
    llm_model: str = "qwen2.5:7b"
    ollama_url: str = "http://127.0.0.1:11434"
    openai_compat_base_url: str = ""
    openai_compat_api_key: str = ""
    llm_cache_path: str = "llm_cache.jsonl"

    # mongo: persist runs (default). memory: keep runs in the process (tests, quick dev).
    storage_mode: Literal["mongo", "memory"] = "mongo"
    log_level: str = "INFO"


settings = Settings()
