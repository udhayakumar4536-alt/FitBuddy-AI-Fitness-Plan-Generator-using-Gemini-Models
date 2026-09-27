from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    app_name: str = "FitBuddy"

    database_url: str = "sqlite:///./fitbuddy.db"

    gemini_api_key: str = ""

    gemini_workout_model: str = "gemini-2.5-pro"

    gemini_fast_model: str = "gemini-2.5-flash"

    demo_mode: bool = True

    admin_token: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache
def get_settings():

    return Settings()


settings = get_settings()