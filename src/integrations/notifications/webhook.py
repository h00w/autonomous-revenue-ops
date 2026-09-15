from __future__ import annotations

from urllib.parse import urlparse

import httpx

from ..http import BoundedHttpClient
from ..models import NotificationResult, OutboundWebhook


class OutboundWebhookAdapter:
    """Generic HTTPS webhook adapter for SaaS and workflow integrations."""

    provider = "webhook"

    def __init__(
        self,
        *,
        client: httpx.Client | None = None,
        allow_http_for_tests: bool = False,
    ) -> None:
        self.allow_http_for_tests = allow_http_for_tests
        self.http = BoundedHttpClient(self.provider, client=client)

    def close(self) -> None:
        self.http.close()

    def send(self, event: OutboundWebhook) -> NotificationResult:
        url = str(event.url)
        parsed = urlparse(url)
        if parsed.scheme != "https" and not self.allow_http_for_tests:
            raise ValueError("Outbound webhooks must use HTTPS")
        headers = {"Content-Type": "application/json", **event.headers}
        response = self.http.request(
            "POST",
            url,
            headers=headers,
            json={
                "event_type": event.event_type,
                "payload": event.payload,
            },
            expected_statuses={200, 201, 202, 204},
        )
        return NotificationResult(
            provider=self.provider,
            delivered=True,
            provider_message_id=(
                response.headers.get("X-Request-ID")
                or response.headers.get("X-Correlation-ID")
            ),
            status_code=response.status_code,
        )
