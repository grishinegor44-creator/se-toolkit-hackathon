from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    database_url: str = "postgresql+asyncpg://cocktail:cocktail@db:5432/cocktaildb"

    # External API
    cocktaildb_base_url: str = "https://www.thecocktaildb.com/api/json/v1/1"
    cocktaildb_rate_limit_ms: int = 1000  # Minimum ms between requests

    # LLM (optional)
    llm_enabled: bool = False
    llm_api_key: Optional[str] = None
    llm_api_base_url: str = "https://openrouter.ai/api/v1"
    llm_api_model: str = "openai/gpt-4o-mini"

    # App
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False


settings = Settings()
