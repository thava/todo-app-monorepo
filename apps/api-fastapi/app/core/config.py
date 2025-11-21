"""Application configuration management."""

import secrets
from typing import Annotated, Any, Literal

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    HttpUrl,
    PostgresDsn,
    computed_field,
    field_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> list[str] | str:
    """Parse CORS origins from comma-separated string or list."""
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",") if i.strip()]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
        case_sensitive=False,
    )

    # Environment
    NODE_ENV: Literal["development", "production", "test"] = "development"

    # API Configuration
    PROJECT_NAME: str = "Todo App API"
    API_V1_STR: str = "/api/v1"
    FASTAPI_PORT: int = 8000
    FASTAPI_URL: str = "http://localhost:8000"

    # CORS
    CORS_ALLOWED_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        """Get all CORS origins including defaults."""
        origins = [str(origin).rstrip("/") for origin in self.CORS_ALLOWED_ORIGINS]
        return origins

    # Database
    DATABASE_URL: PostgresDsn | None = None
    FASTAPI_DATABASE_URL: PostgresDsn | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def db_url(self) -> PostgresDsn:
        """Get the database URL, preferring FASTAPI_DATABASE_URL over DATABASE_URL."""
        if self.FASTAPI_DATABASE_URL:
            return self.FASTAPI_DATABASE_URL
        if self.DATABASE_URL:
            return self.DATABASE_URL
        raise ValueError("Either FASTAPI_DATABASE_URL or DATABASE_URL must be set")

    # JWT Configuration
    JWT_ACCESS_SECRET: str
    JWT_REFRESH_SECRET: str
    JWT_ACCESS_EXPIRY: str = "15m"  # 15 minutes
    JWT_REFRESH_EXPIRY: str = "7d"  # 7 days

    @field_validator("JWT_ACCESS_SECRET", "JWT_REFRESH_SECRET", mode="before")
    @classmethod
    def validate_jwt_secrets(cls, v: str | None) -> str:
        """Validate JWT secrets are set."""
        if not v:
            # Generate a random secret for development
            return secrets.token_urlsafe(32)
        return v

    # Email Configuration (SendGrid or SMTP)
    SENDGRID_API_KEY: str | None = None
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASS: str | None = None
    SMTP_SECURE: bool = False

    EMAIL_FROM: EmailStr | None = None
    EMAIL_FROM_NAME: str | None = None
    EMAIL_REPLY_TO: EmailStr | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def emails_enabled(self) -> bool:
        """Check if email sending is enabled."""
        return bool(self.SENDGRID_API_KEY or (self.SMTP_HOST and self.SMTP_USER))

    # Frontend Configuration
    FRONTEND_HOST: str = "http://localhost:4000"

    # Sentry (Optional)
    SENTRY_DSN: HttpUrl | None = None

    # Development Features
    ENABLE_DEV_REVERSIBLE_PASSWORDS: bool = False
    DEV_REVERSIBLE_PASSWORD_KEY: str | None = None

    # Logging
    LOG_LEVEL: Literal["debug", "info", "warning", "error", "critical"] = "info"

    # Metrics
    ENABLE_METRICS: bool = False

    # Demo Configuration (for development/testing)
    DEMO_DOMAIN: str | None = None
    DEMO_PASSWORD: str | None = None
    DEMO_USERS: str | None = None


settings = Settings()  # type: ignore[call-arg]
