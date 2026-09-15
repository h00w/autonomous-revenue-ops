from src.config import Settings
from src.idempotency import InMemoryIdempotencyStore, derive_idempotency_key
from src.models import LeadEvaluationRequest, LeadInput, Qualification
from src.service import RevenueOpsService


def request_fixture() -> LeadEvaluationRequest:
    return LeadEvaluationRequest(
        lead=LeadInput(
            lead_id="lead_phase1",
            name="Ada Example",
            email="ada@example.com",
            company="Example AB",
            role="VP Revenue",
            consent_to_contact=True,
        ),
        qualification=Qualification(
            score=88,
            confidence=0.93,
            icp_fit=91,
            intent=86,
            urgency=75,
            evidence=["Synthetic regression evidence"],
        ),
    )


def test_derived_idempotency_key_is_deterministic():
    body = request_fixture()
    assert derive_idempotency_key(body) == derive_idempotency_key(body)
    assert derive_idempotency_key(body).startswith("idem_")


def test_service_replays_cached_result_for_same_key():
    settings = Settings(environment="test", idempotency_ttl_seconds=60)
    store = InMemoryIdempotencyStore(ttl_seconds=60)
    service = RevenueOpsService(settings=settings, idempotency_store=store)
    body = request_fixture()

    first = service.process(body, correlation_id="corr_test", idempotency_key="idem_test")
    second = service.process(body, correlation_id="corr_other", idempotency_key="idem_test")

    assert first.replayed is False
    assert second.replayed is True
    assert first.event.event_id == second.event.event_id
    assert first.event.correlation_id == second.event.correlation_id == "corr_test"
    assert len(store) == 1


def test_service_generates_event_and_policy_result():
    service = RevenueOpsService(settings=Settings(environment="test"))
    result = service.process(request_fixture(), correlation_id="corr_phase1")

    assert result.event.event_type == "lead.evaluation.completed"
    assert result.event.correlation_id == "corr_phase1"
    assert result.event.payload["decision"] == "AUTO_ROUTE"
    assert result.policy.authorized_for_outreach is True
