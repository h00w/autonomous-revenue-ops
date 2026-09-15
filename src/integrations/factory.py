from typing import Literal

import httpx

from ..config import Settings
from .crm.base import CRMAdapter
from .crm.hubspot import HubSpotCRMAdapter
from .crm.salesforce import SalesforceCRMAdapter
from .notifications.email import SMTPEmailAdapter
from .notifications.slack import SlackWebhookNotifier

CRMProvider = Literal["hubspot", "salesforce"]


def build_crm_adapter(
    settings: Settings,
    provider: CRMProvider,
    *,
    client: httpx.Client | None = None,
) -> CRMAdapter:
    if provider == "hubspot":
        if settings.hubspot_access_token is None:
            raise ValueError("ARO_HUBSPOT_ACCESS_TOKEN is required for HubSpot")
        return HubSpotCRMAdapter(
            settings.hubspot_access_token.get_secret_value(),
            base_url=settings.hubspot_base_url,
            client=client,
            allowed_custom_properties=settings.comma_separated(
                settings.hubspot_custom_properties
            ),
        )

    if settings.salesforce_instance_url is None:
        raise ValueError("ARO_SALESFORCE_INSTANCE_URL is required for Salesforce")
    if settings.salesforce_access_token is None:
        raise ValueError("ARO_SALESFORCE_ACCESS_TOKEN is required for Salesforce")
    return SalesforceCRMAdapter(
        settings.salesforce_instance_url,
        settings.salesforce_access_token.get_secret_value(),
        api_root=settings.salesforce_api_root,
        client=client,
        allowed_custom_fields=settings.comma_separated(
            settings.salesforce_custom_fields
        ),
    )


def build_slack_notifier(
    settings: Settings,
    *,
    client: httpx.Client | None = None,
) -> SlackWebhookNotifier:
    if settings.slack_webhook_url is None:
        raise ValueError("ARO_SLACK_WEBHOOK_URL is required for Slack")
    return SlackWebhookNotifier(
        settings.slack_webhook_url.get_secret_value(),
        client=client,
    )


def build_smtp_adapter(settings: Settings) -> SMTPEmailAdapter:
    if settings.smtp_host is None:
        raise ValueError("ARO_SMTP_HOST is required for SMTP")
    if settings.smtp_from_email is None:
        raise ValueError("ARO_SMTP_FROM_EMAIL is required for SMTP")
    return SMTPEmailAdapter(
        host=settings.smtp_host,
        port=settings.smtp_port,
        from_email=settings.smtp_from_email,
        username=settings.smtp_username,
        password=(
            settings.smtp_password.get_secret_value()
            if settings.smtp_password is not None
            else None
        ),
        use_starttls=settings.smtp_use_starttls,
    )
