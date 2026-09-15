import hmac
from typing import Annotated

from fastapi import Header, HTTPException

from ..config import get_settings


def require_workflow_api_key(
    supplied: Annotated[str | None, Header(alias="X-ARO-API-Key")] = None,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> None:
    """Require the configured workflow API key.

    Existing clients may send ``X-ARO-API-Key``. Standards-oriented clients
    such as Grafana Cloud can instead send ``Authorization: Bearer <key>``.
    Both mechanisms are checked against the same secret and neither changes
    the underlying authorization boundary.
    """
    settings = get_settings()
    configured = settings.workflow_api_key
    if configured is None:
        if settings.environment == "production":
            raise HTTPException(status_code=503, detail="Workflow API authentication is not configured")
        return

    candidate = supplied
    if candidate is None and authorization:
        scheme, separator, token = authorization.partition(" ")
        if separator and scheme.lower() == "bearer" and token:
            candidate = token

    if candidate is None or not hmac.compare_digest(
        candidate, configured.get_secret_value()
    ):
        raise HTTPException(status_code=401, detail="Invalid workflow API key")
