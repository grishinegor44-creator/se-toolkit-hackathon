from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class BotSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram
    bot_token: str

    # Backend
    backend_url: str = "http://backend:8000"

    # LLM (optional)
    llm_enabled: bool = False
    llm_api_key: Optional[str] = None
    llm_api_base_url: str = "https://openrouter.ai/api/v1"
    llm_api_model: str = "openai/gpt-4o-mini"

    # Misc
    debug: bool = False


settings = BotSettings()
