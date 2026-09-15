from functools import lru_cache
from typing import Literal, Optional

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables.

    Environment variables are prefixed with ``ARO_``. Secrets use Pydantic
    ``SecretStr`` so accidental model/log rendering does not expose values.
    """

    app_name: str = "Autonomous Revenue Ops"
    service_version: str = "0.3.0"
    environment: Literal["development", "test", "staging", "production"] = "development"
    api_prefix: str = "/v1"
    log_level: str = "INFO"
    idempotency_ttl_seconds: int = 3600

    # HubSpot CRM
    hubspot_access_token: Optional[SecretStr] = None
    hubspot_base_url: str = "https://api.hubapi.com"
    hubspot_custom_properties: str = ""

    # Salesforce CRM
    salesforce_instance_url: Optional[str] = None
    salesforce_access_token: Optional[SecretStr] = None
    salesforce_api_root: str = "/services/data/latest"
    salesforce_custom_fields: str = ""

    # Slack incoming webhook
    slack_webhook_url: Optional[SecretStr] = None

    # SMTP email
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[SecretStr] = None
    smtp_from_email: Optional[str] = None
    smtp_use_starttls: bool = True

    # AI providers. Model IDs are configuration, not business logic.
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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="ARO_",
        extra="ignore",
        case_sensitive=False,
    )

    @staticmethod
    def comma_separated(value: str) -> set[str]:
        return {item.strip() for item in value.split(",") if item.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
