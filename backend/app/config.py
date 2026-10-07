from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    mongo_uri: str = "mongodb://127.0.0.1:27017"
    mongo_db: str = "securemcp"
    llm_mode: str = "replay"  # replay | ollama | openai_compat


settings = Settings()
