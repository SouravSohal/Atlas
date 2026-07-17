from functools import lru_cache
import os
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator, model_validator
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

    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(
        default=DEFAULT_APP_NAME,
        validation_alias=AliasChoices("APP__NAME", "APP_NAME"),
        description="Name of the application.",
    )
    version: str = Field(
        default=DEFAULT_APP_VERSION,
        validation_alias=AliasChoices("APP__VERSION", "APP_VERSION"),
        description="Version of the application.",
    )
    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        validation_alias=AliasChoices("APP__ENVIRONMENT", "ENVIRONMENT", "APP_ENV"),
        description="Target environment.",
    )
    debug: bool = Field(
        default=False,
        validation_alias=AliasChoices("APP__DEBUG", "APP_DEBUG"),
        description="Enable debug mode.",
    )

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        """Validates that application name is not empty."""
        if not v.strip():
            raise ValueError("Application name cannot be empty")
        return v


class ApiSettings(BaseModel):
    """API-related configuration settings."""

    model_config = ConfigDict(populate_by_name=True)

    host: str = Field(
        default=DEFAULT_HOST,
        validation_alias=AliasChoices("API__HOST", "API_HOST"),
        description="Host to bind the API server to.",
    )
    port: int = Field(
        default=DEFAULT_PORT,
        validation_alias=AliasChoices("API__PORT", "API_PORT"),
        description="Port to bind the API server to.",
    )
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173"],
        validation_alias=AliasChoices("API__CORS_ORIGINS", "API_CORS_ORIGINS"),
        description="Allowed CORS origins.",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        """Parses allowed CORS origins, splitting comma-separated strings and rejecting wildcards."""
        if isinstance(v, str):
            v = [item.strip() for item in v.split(",") if item.strip()]
        if not isinstance(v, list):
            v = [str(v)]
        # Reject "*" wildcard to prevent security vulnerabilities
        if "*" in v or any(item == "*" for item in v):
            raise ValueError("Wildcard '*' is not allowed in CORS origins. Explicitly configure allowed origins.")
        return v

    @field_validator("port")
    @classmethod
    def port_range(cls, v: int) -> int:
        """Validates that the port falls within valid network boundaries."""
        if not (1 <= v <= 65535):
            raise ValueError("Port must be between 1 and 65535")
        return v


class GoogleCloudSettings(BaseModel):
    """Google Cloud configuration settings."""

    model_config = ConfigDict(populate_by_name=True)

    project_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("GCP__PROJECT_ID", "GOOGLE_CLOUD_PROJECT"),
        description="Google Cloud Project ID.",
    )
    credentials_path: str | None = Field(
        default=None,
        validation_alias=AliasChoices("GCP__CREDENTIALS_PATH", "GOOGLE_APPLICATION_CREDENTIALS"),
        description="Path to GCP service account key JSON.",
    )


class FirestoreSettings(BaseModel):
    """Firestore configuration settings."""

    model_config = ConfigDict(populate_by_name=True)

    database: str = Field(
        default="(default)",
        validation_alias=AliasChoices("FIRESTORE__DATABASE", "FIRESTORE_DATABASE"),
        description="Firestore database name.",
    )
    emulator_host: str | None = Field(
        default=None,
        validation_alias=AliasChoices("FIRESTORE__EMULATOR_HOST", "FIRESTORE_EMULATOR_HOST"),
        description="Firestore emulator host connection string.",
    )


class GeminiSettings(BaseModel):
    """Google Gemini AI integration settings."""

    model_config = ConfigDict(populate_by_name=True)

    api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("GEMINI__API_KEY", "GEMINI_API_KEY"),
        description="API Key for Gemini model access.",
    )
    model_name: str = Field(
        default="gemini-2.5-flash",
        validation_alias=AliasChoices("GEMINI__MODEL_NAME", "GEMINI_MODEL"),
        description="Gemini model identifier to use.",
    )


class FirebaseSettings(BaseModel):
    """Firebase integration settings."""

    model_config = ConfigDict(populate_by_name=True)

    web_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("FIREBASE__WEB_API_KEY", "FIREBASE_WEB_API_KEY"),
        description="Firebase Web API Key.",
    )
    auth_domain: str | None = Field(
        default=None,
        validation_alias=AliasChoices("FIREBASE__AUTH_DOMAIN", "FIREBASE_AUTH_DOMAIN"),
        description="Firebase auth domain.",
    )


class SecuritySettings(BaseModel):
    """API security and cryptography settings."""

    model_config = ConfigDict(populate_by_name=True)

    secret_key: str = Field(
        default="",
        validation_alias=AliasChoices("SECURITY__SECRET_KEY", "JWT_SECRET"),
        description="Secret key for signing tokens.",
    )
    token_expire_minutes: int = Field(
        default=60,
        validation_alias=AliasChoices("SECURITY__TOKEN_EXPIRE_MINUTES", "JWT_EXPIRE_MINUTES"),
        description="Access token lifetime in minutes.",
    )

    @field_validator("secret_key")
    @classmethod
    def secret_key_not_empty(cls, v: str) -> str:
        """Validates that secret key is not empty."""
        if not v or not v.strip():
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

    model_config = ConfigDict(populate_by_name=True)

    level: str = Field(
        default=DEFAULT_LOG_LEVEL,
        validation_alias=AliasChoices("LOGGING__LEVEL", "LOG_LEVEL"),
        description="Minimal logging level to output.",
    )
    json_format: bool = Field(
        default=False,
        validation_alias=AliasChoices("LOGGING__JSON_FORMAT", "LOG_JSON_FORMAT"),
        description="Whether to format logs as structured JSON.",
    )

    @field_validator("level")
    @classmethod
    def valid_level(cls, v: str) -> str:
        """Validates standard syslog logging levels."""
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in allowed:
            raise ValueError(f"Logging level must be one of {allowed}")
        return v.upper()


class DemoSettings(BaseModel):
    """Demonstration configuration settings."""

    model_config = ConfigDict(populate_by_name=True)

    mode: bool = Field(
        default=False,
        validation_alias=AliasChoices("DEMO_MODE"),
        description="Whether demo mode is enabled."
    )
    email: str = Field(
        default="",
        validation_alias=AliasChoices("DEMO_EMAIL"),
        description="Demo account email."
    )
    password: str = Field(
        default="",
        validation_alias=AliasChoices("DEMO_PASSWORD"),
        description="Demo account password."
    )
    role: str = Field(
        default="Administrator",
        validation_alias=AliasChoices("DEMO_ROLE"),
        description="Demo account role."
    )


class RateLimitSettings(BaseModel):
    """Configuration settings for production-grade rate limiting."""

    model_config = ConfigDict(populate_by_name=True)

    auth: str = Field(
        default="5/minute",
        validation_alias=AliasChoices("RATE_LIMIT_AUTH"),
        description="Rate limit for authentication endpoints.",
    )
    copilot: str = Field(
        default="10/minute",
        validation_alias=AliasChoices("RATE_LIMIT_COPILOT"),
        description="Rate limit for copilot assistant.",
    )
    ai: str = Field(
        default="20/minute",
        validation_alias=AliasChoices("RATE_LIMIT_AI"),
        description="Rate limit for intelligence/AI endpoints.",
    )
    simulation: str = Field(
        default="30/minute",
        validation_alias=AliasChoices("RATE_LIMIT_SIMULATION"),
        description="Rate limit for simulation demo controls.",
    )
    ws: str = Field(
        default="10/minute",
        validation_alias=AliasChoices("RATE_LIMIT_WS"),
        description="Rate limit for WebSocket handshakes.",
    )
    default: str = Field(
        default="60/minute",
        validation_alias=AliasChoices("RATE_LIMIT_DEFAULT"),
        description="Default rate limit fallback.",
    )


class CacheSettings(BaseModel):
    """Configuration settings for lightweight response caching."""

    model_config = ConfigDict(populate_by_name=True)

    overview_ttl: int = Field(
        default=60,
        validation_alias=AliasChoices("CACHE_TTL_OVERVIEW"),
        description="TTL in seconds for dashboard overview cache.",
    )
    operational_state_ttl: int = Field(
        default=30,
        validation_alias=AliasChoices("CACHE_TTL_OPERATIONAL_STATE"),
        description="TTL in seconds for operational state cache.",
    )
    metrics_ttl: int = Field(
        default=60,
        validation_alias=AliasChoices("CACHE_TTL_METRICS"),
        description="TTL in seconds for dashboard metrics cache.",
    )
    briefing_ttl: int = Field(
        default=300,
        validation_alias=AliasChoices("CACHE_TTL_BRIEFING"),
        description="TTL in seconds for situation briefings cache.",
    )


class Settings(BaseSettings):
    """Global configuration settings for the application, loaded from env files and environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
        populate_by_name=True,
    )

    app: ApplicationSettings = Field(default_factory=ApplicationSettings)
    api: ApiSettings = Field(default_factory=ApiSettings)
    gcp: GoogleCloudSettings = Field(default_factory=GoogleCloudSettings)
    firestore: FirestoreSettings = Field(default_factory=FirestoreSettings)
    gemini: GeminiSettings = Field(default_factory=GeminiSettings)
    firebase: FirebaseSettings = Field(default_factory=FirebaseSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    demo: DemoSettings = Field(default_factory=DemoSettings)
    rate_limits: RateLimitSettings = Field(default_factory=RateLimitSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)

    @model_validator(mode="before")
    @classmethod
    def map_flat_env_vars(cls, data: Any) -> Any:
        """Bridges flat environment variables into their nested configuration fields."""
        if not isinstance(data, dict):
            data = {}

        # 1. Map JWT_SECRET / SECURITY__SECRET_KEY to security.secret_key
        jwt_secret = os.environ.get("JWT_SECRET") or os.environ.get("SECURITY__SECRET_KEY")
        if jwt_secret:
            if "security" not in data:
                data["security"] = {}
            if isinstance(data["security"], dict) and "secret_key" not in data["security"]:
                data["security"]["secret_key"] = jwt_secret

        # 2. Map DEMO_EMAIL & DEMO_PASSWORD to demo config
        demo_email = os.environ.get("DEMO_EMAIL")
        if demo_email:
            if "demo" not in data:
                data["demo"] = {}
            if isinstance(data["demo"], dict) and "email" not in data["demo"]:
                data["demo"]["email"] = demo_email

        demo_password = os.environ.get("DEMO_PASSWORD")
        if demo_password:
            if "demo" not in data:
                data["demo"] = {}
            if isinstance(data["demo"], dict) and "password" not in data["demo"]:
                data["demo"]["password"] = demo_password

        # 3. Map GEMINI_API_KEY to gemini.api_key
        gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI__API_KEY")
        if gemini_key:
            if "gemini" not in data:
                data["gemini"] = {}
            if isinstance(data["gemini"], dict) and "api_key" not in data["gemini"]:
                data["gemini"]["api_key"] = gemini_key

        return data

    @model_validator(mode="after")
    def validate_secrets_and_credentials(self) -> 'Settings':
        """Enforces security checks on critical keys and demo credentials at startup."""
        placeholders = {
            "change-me",
            "change-me-in-production-use-strong-secret",
            "change-me-in-production-use-strong-secret-phrase-here",
            "password",
            "secret",
            "test",
            "demo",
            "mock-api-key-replace-in-production",
        }

        # 1. Validate security.secret_key (JWT Secret)
        sec_key = self.security.secret_key
        if not sec_key or not sec_key.strip():
            raise ValueError(
                "Security secret key (SECURITY__SECRET_KEY / JWT_SECRET) is missing or empty. "
                "Please configure a strong secret key in your environment variables."
            )
        
        sec_key_clean = sec_key.strip().lower()
        if sec_key_clean in placeholders or any(p == sec_key_clean for p in placeholders):
            raise ValueError(
                f"Security secret key (SECURITY__SECRET_KEY / JWT_SECRET) cannot use insecure placeholder value: '{sec_key}'"
            )

        # 2. Validate Demo Credentials
        is_prod = self.app.environment == Environment.PRODUCTION
        is_dev = self.app.environment == Environment.DEVELOPMENT
        is_demo = self.demo.mode

        if is_prod:
            if not self.demo.password or not self.demo.password.strip():
                raise ValueError("Production configuration error: DEMO_PASSWORD must be explicitly configured in Production.")
            if not self.demo.email or not self.demo.email.strip():
                raise ValueError("Production configuration error: DEMO_EMAIL must be explicitly configured in Production.")
        
        if is_demo or is_dev:
            if not self.demo.password or not self.demo.password.strip():
                raise ValueError("Demo/Development configuration error: DEMO_PASSWORD must be explicitly configured in Development or Demo mode.")
            if not self.demo.email or not self.demo.email.strip():
                raise ValueError("Demo/Development configuration error: DEMO_EMAIL must be explicitly configured in Development or Demo mode.")

        if self.demo.password:
            demo_pass_clean = self.demo.password.strip().lower()
            if demo_pass_clean in placeholders or demo_pass_clean == "demo-secure-pass-1234":
                raise ValueError(
                    f"Demo password cannot use insecure placeholder or default value: '{self.demo.password}'"
                )

        return self


@lru_cache
def get_settings() -> Settings:
    """Returns the cached singleton instance of the global settings."""
    return Settings()
