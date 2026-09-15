from functools import lru_cache
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import ValidationError

from ..config import get_settings
from ..orchestration.models import StartLeadWorkflowRequest, WorkflowRunResponse
from ..orchestration.runtime import get_workflow_orchestrator
from .webhooks import SQLiteReplayProtector, WebhookSignatureError, WebhookVerifier

router = APIRouter(prefix="/v1/webhooks", tags=["webhooks"])


@lru_cache
def _verifier() -> WebhookVerifier:
    settings = get_settings()
    if settings.webhook_signing_secret is None:
        raise ValueError("Webhook signing secret is not configured")
    return WebhookVerifier(
        settings.webhook_signing_secret.get_secret_value(),
        SQLiteReplayProtector(settings.security_db_path),
        max_skew_seconds=settings.webhook_max_skew_seconds,
    )


@router.post("/lead", response_model=WorkflowRunResponse)
async def signed_lead_webhook(
    request: Request,
    timestamp: Annotated[str | None, Header(alias="X-ARO-Timestamp")] = None,
    signature: Annotated[str | None, Header(alias="X-ARO-Signature")] = None,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> WorkflowRunResponse:
    if timestamp is None or signature is None:
        raise HTTPException(status_code=401, detail="Missing webhook signature headers")
    body = await request.body()
    try:
        _verifier().verify(body, timestamp, signature)
    except ValueError as exc:
        if isinstance(exc, WebhookSignatureError):
            raise HTTPException(status_code=401, detail=str(exc)) from exc
        raise HTTPException(status_code=503, detail="Webhook verification is not configured") from exc
    try:
        payload = StartLeadWorkflowRequest.model_validate_json(body)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail="Invalid workflow webhook payload") from exc
    try:
        orchestrator = get_workflow_orchestrator()
    except ValueError as exc:
        raise HTTPException(status_code=503, detail="Workflow AI runtime is not configured") from exc
    return orchestrator.start(
        payload,
        correlation_id=request.state.correlation_id,
        idempotency_key=idempotency_key,
    )
