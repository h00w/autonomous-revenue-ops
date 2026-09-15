import json

import httpx
import pytest

from src.integrations.models import EmailMessage, OutboundWebhook
from src.integrations.notifications.email import SMTPEmailAdapter
from src.integrations.notifications.slack import SlackWebhookNotifier
from src.integrations.notifications.webhook import OutboundWebhookAdapter


def test_slack_incoming_webhook_payload():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.host == "hooks.slack.com"
        assert json.loads(request.content) == {"text": "Lead requires review"}
        return httpx.Response(200, text="ok", request=request)

    notifier = SlackWebhookNotifier(
        "https://hooks.slack.com/services/T/B/X",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    result = notifier.send("Lead requires review")
    assert result.delivered is True
    assert result.status_code == 200


def test_slack_rejects_non_slack_webhook_host():
    with pytest.raises(ValueError):
        SlackWebhookNotifier("https://example.com/webhook")


def test_generic_webhook_posts_event_envelope():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["x-source"] == "aro"
        assert json.loads(request.content) == {
            "event_type": "lead.qualified",
            "payload": {"lead_id": "lead_1"},
        }
        return httpx.Response(
            202,
            headers={"X-Request-ID": "req_123"},
            request=request,
        )

    adapter = OutboundWebhookAdapter(
        client=httpx.Client(transport=httpx.MockTransport(handler))
    )
    result = adapter.send(
        OutboundWebhook(
            url="https://automation.example/webhook",
            event_type="lead.qualified",
            payload={"lead_id": "lead_1"},
            headers={"X-Source": "aro"},
        )
    )
    assert result.delivered is True
    assert result.provider_message_id == "req_123"


class FakeSMTP:
    instances = []

    def __init__(self, host, port, timeout):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.started_tls = False
        self.login_args = None
        self.sent = None
        FakeSMTP.instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def starttls(self, context=None):
        self.started_tls = True

    def login(self, username, password):
        self.login_args = (username, password)

    def send_message(self, message):
        self.sent = message
        return {}


def test_smtp_adapter_sends_bounded_message():
    FakeSMTP.instances.clear()
    adapter = SMTPEmailAdapter(
        host="smtp.example.com",
        port=587,
        from_email="ops@example.com",
        username="user",
        password="secret",
        smtp_factory=FakeSMTP,
    )
    result = adapter.send(
        EmailMessage(
            to="lead@example.com",
            subject="Thanks for your interest",
            text="We received your request.",
            reply_to="sales@example.com",
        )
    )
    smtp = FakeSMTP.instances[-1]
    assert result.delivered is True
    assert smtp.started_tls is True
    assert smtp.login_args == ("user", "secret")
    assert smtp.sent["From"] == "ops@example.com"
    assert smtp.sent["To"] == "lead@example.com"
    assert smtp.sent["Reply-To"] == "sales@example.com"
