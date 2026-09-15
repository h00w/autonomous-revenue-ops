from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables.

    Environment variables are prefixed with ``ARO_``. Example:
    ``ARO_ENVIRONMENT=staging``.
    """

    app_name: str = "Autonomous Revenue Ops"
    service_version: str = "0.1.0"
    environment: Literal["development", "test", "staging", "production"] = "development"
    api_prefix: str = "/v1"
    log_level: str = "INFO"
    idempotency_ttl_seconds: int = 3600

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="ARO_",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
