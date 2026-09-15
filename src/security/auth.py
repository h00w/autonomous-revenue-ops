import hmac
from typing import Annotated

from fastapi import Header, HTTPException

from ..config import get_settings


def require_workflow_api_key(
    supplied: Annotated[str | None, Header(alias="X-ARO-API-Key")] = None,
) -> None:
    settings = get_settings()
    configured = settings.workflow_api_key
    if configured is None:
        if settings.environment == "production":
            raise HTTPException(status_code=503, detail="Workflow API authentication is not configured")
        return
    if supplied is None or not hmac.compare_digest(supplied, configured.get_secret_value()):
        raise HTTPException(status_code=401, detail="Invalid workflow API key")
