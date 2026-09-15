from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

import httpx

from ..http import BoundedHttpClient
from ..models import NotificationResult


class SlackWebhookNotifier:
    """One-way Slack notifier using an incoming webhook URL."""

    provider = "slack"

    def __init__(
        self,
        webhook_url: str,
        *,
        client: httpx.Client | None = None,
        allow_non_slack_host: bool = False,
    ) -> None:
        parsed = urlparse(webhook_url)
        if parsed.scheme != "https":
            raise ValueError("Slack webhook URL must use https://")
        allowed_hosts = {"hooks.slack.com", "hooks.slack-gov.com"}
        if not allow_non_slack_host and parsed.hostname not in allowed_hosts:
            raise ValueError("Slack webhook URL must use an approved Slack webhook host")
        self.webhook_url = webhook_url
        self.http = BoundedHttpClient(self.provider, client=client)

    def close(self) -> None:
        self.http.close()

    def send(self, text: str, *, blocks: list[dict[str, Any]] | None = None) -> NotificationResult:
        payload: dict[str, Any] = {"text": text}
        if blocks:
            payload["blocks"] = blocks
        response = self.http.request(
            "POST",
            self.webhook_url,
            headers={"Content-Type": "application/json"},
            json=payload,
            expected_statuses={200},
        )
        return NotificationResult(
            provider=self.provider,
            delivered=True,
            status_code=response.status_code,
        )
