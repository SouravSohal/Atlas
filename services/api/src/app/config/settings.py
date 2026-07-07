from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "ATLAS API"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False
    port: int = 8000
    host: str = "0.0.0.0"
