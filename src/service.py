import logging
from uuid import uuid4

from .config import Settings, get_settings
from .idempotency import InMemoryIdempotencyStore, derive_idempotency_key
from .models import EventEnvelope, LeadEvaluationRequest, WorkflowResponse
from .policy import evaluate_policy

logger = logging.getLogger(__name__)


class RevenueOpsService:
    """Application service coordinating validation, policy and event metadata."""

    def __init__(
        self,
        settings: Settings | None = None,
        idempotency_store: InMemoryIdempotencyStore | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.idempotency_store = idempotency_store or InMemoryIdempotencyStore(
            ttl_seconds=self.settings.idempotency_ttl_seconds
        )

    def process(
        self,
        request: LeadEvaluationRequest,
        *,
        correlation_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> WorkflowResponse:
        correlation_id = correlation_id or f"corr_{uuid4().hex}"
        idempotency_key = idempotency_key or derive_idempotency_key(request)

        cached = self.idempotency_store.get(idempotency_key)
        if cached is not None:
            logger.info(
                "idempotent replay",
                extra={
                    "correlation_id": cached.event.correlation_id,
                    "event_id": cached.event.event_id,
                    "idempotency_key": idempotency_key,
                    "decision": cached.policy.decision.value,
                },
            )
            return cached.model_copy(update={"replayed": True})

        policy = evaluate_policy(request.lead, request.qualification)
        event = EventEnvelope(
            event_id=f"evt_{uuid4().hex}",
            event_type="lead.evaluation.completed",
            correlation_id=correlation_id,
            idempotency_key=idempotency_key,
            payload={
                "lead_id": request.lead.lead_id,
                "source": request.lead.source,
                "decision": policy.decision.value,
                "authorized_for_outreach": policy.authorized_for_outreach,
            },
        )
        response = WorkflowResponse(event=event, policy=policy)
        self.idempotency_store.put(idempotency_key, response)

        logger.info(
            "lead evaluation completed",
            extra={
                "correlation_id": correlation_id,
                "event_id": event.event_id,
                "idempotency_key": idempotency_key,
                "lead_id": request.lead.lead_id,
                "decision": policy.decision.value,
                "authorized_for_outreach": policy.authorized_for_outreach,
            },
        )
        return response

    def readiness_checks(self) -> dict[str, str]:
        return {
            "policy_engine": "ok",
            "idempotency_store": "ok",
            "configuration": "ok",
        }
