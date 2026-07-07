from functools import lru_cache

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config.constants import (
    DEFAULT_APP_NAME,
    DEFAULT_APP_VERSION,
    DEFAULT_HOST,
    DEFAULT_LOG_LEVEL,
    DEFAULT_PORT,
)
from app.config.environment import Environment


class ApplicationSettings(BaseModel):
    """Core application settings."""

    name: str = Field(default=DEFAULT_APP_NAME, description="Name of the application.")
    version: str = Field(default=DEFAULT_APP_VERSION, description="Version of the application.")
    environment: Environment = Field(default=Environment.DEVELOPMENT, description="Target environment.")
    debug: bool = Field(default=False, description="Enable debug mode.")

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        """Validates that application name is not empty."""
        if not v.strip():
            raise ValueError("Application name cannot be empty")
        return v

class ApiSettings(BaseModel):
    """API-related configuration settings."""

    host: str = Field(default=DEFAULT_HOST, description="Host to bind the API server to.")
    port: int = Field(default=DEFAULT_PORT, description="Port to bind the API server to.")
    cors_origins: list[str] = Field(
        default_factory=lambda: ["*"], description="Allowed CORS origins."
    )

    @field_validator("port")
    @classmethod
    def port_range(cls, v: int) -> int:
        """Validates that the port falls within valid network boundaries."""
        if not (1 <= v <= 65535):
            raise ValueError("Port must be between 1 and 65535")
        return v

class GoogleCloudSettings(BaseModel):
    """Google Cloud configuration settings."""

    project_id: str | None = Field(default=None, description="Google Cloud Project ID.")
    credentials_path: str | None = Field(
        default=None, description="Path to GCP service account key JSON."
    )

class FirestoreSettings(BaseModel):
    """Firestore configuration settings."""

    database: str = Field(default="(default)", description="Firestore database name.")
    emulator_host: str | None = Field(
        default=None, description="Firestore emulator host connection string."
    )

class GeminiSettings(BaseModel):
    """Google Gemini AI integration settings."""

    api_key: str | None = Field(default=None, description="API Key for Gemini model access.")
    model_name: str = Field(default="gemini-pro", description="Gemini model identifier to use.")

class FirebaseSettings(BaseModel):
    """Firebase integration settings."""

    web_api_key: str | None = Field(default=None, description="Firebase Web API Key.")
    auth_domain: str | None = Field(default=None, description="Firebase auth domain.")

class SecuritySettings(BaseModel):
    """API security and cryptography settings."""

    secret_key: str = Field(
        default="change-me-in-production-use-strong-secret",
        description="Secret key for signing tokens.",
    )
    token_expire_minutes: int = Field(
        default=60, description="Access token lifetime in minutes."
    )

    @field_validator("secret_key")
    @classmethod
    def secret_key_not_empty(cls, v: str) -> str:
        """Validates that secret key is not empty."""
        if not v.strip():
            raise ValueError("Secret key cannot be empty")
        return v

    @field_validator("token_expire_minutes")
    @classmethod
    def positive_expiry(cls, v: int) -> int:
        """Validates that token expiration minutes is positive."""
        if v <= 0:
            raise ValueError("Token expire minutes must be positive")
        return v

class LoggingSettings(BaseModel):
    """Logging settings for the application."""

    level: str = Field(default=DEFAULT_LOG_LEVEL, description="Minimal logging level to output.")
    json_format: bool = Field(default=False, description="Whether to format logs as structured JSON.")

    @field_validator("level")
    @classmethod
    def valid_level(cls, v: str) -> str:
        """Validates standard syslog logging levels."""
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in allowed:
            raise ValueError(f"Logging level must be one of {allowed}")
        return v.upper()

class Settings(BaseSettings):
    """Global configuration settings for the application, loaded from env files and environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    app: ApplicationSettings = Field(default_factory=ApplicationSettings)
    api: ApiSettings = Field(default_factory=ApiSettings)
    gcp: GoogleCloudSettings = Field(default_factory=GoogleCloudSettings)
    firestore: FirestoreSettings = Field(default_factory=FirestoreSettings)
    gemini: GeminiSettings = Field(default_factory=GeminiSettings)
    firebase: FirebaseSettings = Field(default_factory=FirebaseSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)

@lru_cache
def get_settings() -> Settings:
    """Returns the cached singleton instance of the global settings."""
    return Settings()
