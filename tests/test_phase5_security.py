import pytest
from fastapi import HTTPException

from src.config import get_settings
from src.security.auth import require_workflow_api_key
from src.security.webhooks import SQLiteReplayProtector, WebhookSignatureError, WebhookVerifier


def test_signed_webhook_detects_tampering_and_persistent_replay(tmp_path):
    path = str(tmp_path / "security.sqlite3")
    body = b'{"lead":"safe"}'
    verifier = WebhookVerifier(
        "secret",
        SQLiteReplayProtector(path),
        max_skew_seconds=60,
        clock=lambda: 1000.0,
    )
    signature = verifier.sign(body, "1000")
    verifier.verify(body, "1000", signature)

    reopened = WebhookVerifier(
        "secret",
        SQLiteReplayProtector(path),
        max_skew_seconds=60,
        clock=lambda: 1000.0,
    )
    with pytest.raises(WebhookSignatureError, match="replay"):
        reopened.verify(body, "1000", signature)

    fresh_signature = verifier.sign(body, "1001")
    with pytest.raises(WebhookSignatureError, match="mismatch"):
        verifier.verify(b"tampered", "1001", fresh_signature)


def test_signed_webhook_rejects_stale_timestamp(tmp_path):
    verifier = WebhookVerifier(
        "secret",
        SQLiteReplayProtector(str(tmp_path / "security.sqlite3")),
        max_skew_seconds=30,
        clock=lambda: 1000.0,
    )
    body = b"{}"
    signature = verifier.sign(body, "900")
    with pytest.raises(WebhookSignatureError, match="outside"):
        verifier.verify(body, "900", signature)


def test_production_workflow_api_fails_closed_without_auth_config(monkeypatch):
    monkeypatch.setenv("ARO_ENVIRONMENT", "production")
    monkeypatch.delenv("ARO_WORKFLOW_API_KEY", raising=False)
    get_settings.cache_clear()
    with pytest.raises(HTTPException) as caught:
        require_workflow_api_key(None)
    assert caught.value.status_code == 503
    get_settings.cache_clear()


def test_configured_workflow_api_key_is_constant_time_checked(monkeypatch):
    monkeypatch.setenv("ARO_ENVIRONMENT", "production")
    monkeypatch.setenv("ARO_WORKFLOW_API_KEY", "correct-secret")
    get_settings.cache_clear()
    with pytest.raises(HTTPException) as caught:
        require_workflow_api_key("wrong")
    assert caught.value.status_code == 401
    require_workflow_api_key("correct-secret")
    get_settings.cache_clear()
