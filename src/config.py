from functools import lru_cache
from typing import Literal, Optional

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from ARO_-prefixed environment variables."""

    app_name: str = "Autonomous Revenue Ops"
    service_version: str = "0.6.0"
    environment: Literal["development", "test", "staging", "production"] = "development"
    api_prefix: str = "/v1"
    log_level: str = "INFO"
    idempotency_ttl_seconds: int = 3600

    hubspot_access_token: Optional[SecretStr] = None
    hubspot_base_url: str = "https://api.hubapi.com"
    hubspot_custom_properties: str = ""
    salesforce_instance_url: Optional[str] = None
    salesforce_access_token: Optional[SecretStr] = None
    salesforce_api_root: str = "/services/data/latest"
    salesforce_custom_fields: str = ""
    slack_webhook_url: Optional[SecretStr] = None
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[SecretStr] = None
    smtp_from_email: Optional[str] = None
    smtp_use_starttls: bool = True

    ai_provider_order: str = "openai,anthropic,gemini"
    ai_timeout_seconds: float = 30.0
    openai_api_key: Optional[SecretStr] = None
    openai_base_url: str = "https://api.openai.com"
    openai_model: str = "gpt-5.6-terra"
    anthropic_api_key: Optional[SecretStr] = None
    anthropic_base_url: str = "https://api.anthropic.com"
    anthropic_model: str = "claude-sonnet-5"
    gemini_api_key: Optional[SecretStr] = None
    gemini_base_url: str = "https://generativelanguage.googleapis.com"
    gemini_model: str = "gemini-3.8-flash"

    workflow_store_backend: Literal["memory", "sqlite"] = "sqlite"
    workflow_db_path: str = "data/workflows.sqlite3"
    workflow_lease_seconds: int = 60
    workflow_api_key: Optional[SecretStr] = None
    security_db_path: str = "data/security.sqlite3"
    webhook_signing_secret: Optional[SecretStr] = None
    webhook_max_skew_seconds: int = 300
    dead_letter_db_path: str = "data/dead_letters.sqlite3"
    retry_max_attempts: int = 3
    retry_base_delay_seconds: float = 0.25
    circuit_failure_threshold: int = 3
    circuit_recovery_timeout_seconds: float = 30.0

    model_config = SettingsConfigDict(env_file=".env", env_prefix="ARO_", extra="ignore", case_sensitive=False)

    @staticmethod
    def comma_separated(value: str) -> set[str]:
        return {item.strip() for item in value.split(",") if item.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
