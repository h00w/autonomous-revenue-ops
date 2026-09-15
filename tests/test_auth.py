import pytest
from fastapi import HTTPException
from pydantic import SecretStr

from src.config import Settings
from src.security import auth


def _settings() -> Settings:
    return Settings(
        environment="staging",
        workflow_api_key=SecretStr("test-secret"),
    )


def test_workflow_auth_accepts_custom_header(monkeypatch):
    monkeypatch.setattr(auth, "get_settings", _settings)
    auth.require_workflow_api_key(supplied="test-secret", authorization=None)


def test_workflow_auth_accepts_bearer_token(monkeypatch):
    monkeypatch.setattr(auth, "get_settings", _settings)
    auth.require_workflow_api_key(
        supplied=None,
        authorization="Bearer test-secret",
    )


@pytest.mark.parametrize(
    "supplied,authorization",
    [
        (None, None),
        ("wrong", None),
        (None, "Bearer wrong"),
        (None, "Basic test-secret"),
    ],
)
def test_workflow_auth_rejects_invalid_credentials(
    monkeypatch, supplied, authorization
):
    monkeypatch.setattr(auth, "get_settings", _settings)
    with pytest.raises(HTTPException) as exc:
        auth.require_workflow_api_key(
            supplied=supplied,
            authorization=authorization,
        )
    assert exc.value.status_code == 401
