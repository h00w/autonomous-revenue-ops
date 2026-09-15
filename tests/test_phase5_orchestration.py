import pytest

from src.ai.models import QualificationRecommendation, ResearchOutput, SupervisedLeadResult
from src.models import Decision, LeadInput, PolicyResult
from src.orchestration.engine import WorkflowOrchestrator
from src.orchestration.models import (
    ExecutionClaimRequest,
    ExecutionReceipt,
    RecoveryRequest,
    StartLeadWorkflowRequest,
    WorkflowRun,
    WorkflowRunStatus,
)
from src.orchestration.store import InMemoryWorkflowRunStore, SQLiteWorkflowRunStore


class Evaluator:
    def __init__(self):
        self.calls = 0

    def evaluate(self, lead, *, enrichment_context=None, correlation_id=None):
        self.calls += 1
        q = QualificationRecommendation(
            score=90,
            confidence=0.95,
            icp_fit=90,
            intent=90,
            urgency=70,
            risk_flags=[],
            evidence=["synthetic"],
            rationale="synthetic",
        ).to_domain()
        return SupervisedLeadResult(
            lead=lead,
            research=ResearchOutput(
                summary="synthetic",
                evidence=["synthetic"],
                open_questions=[],
                risk_flags=[],
                confidence=0.9,
            ),
            qualification=q,
            qualification_rationale="synthetic",
            policy=PolicyResult(
                decision=Decision.AUTO_ROUTE,
                authorized_for_outreach=True,
                reason="synthetic",
                next_action="execute",
            ),
            traces=[],
        )


def _lead() -> LeadInput:
    return LeadInput(
        lead_id="lead_phase5",
        name="Grace Hopper",
        email="grace@example.com",
        company="Compiler Systems AB",
        role="CTO",
        message="Interested in governed automation",
        consent_to_contact=True,
    )


def test_recovery_replays_only_persisted_running_stage(tmp_path):
    store = SQLiteWorkflowRunStore(str(tmp_path / "workflows.sqlite3"))
    run = WorkflowRun(
        run_id="run_stalled",
        correlation_id="corr_stalled",
        idempotency_key="idem_stalled",
        status=WorkflowRunStatus.RUNNING,
        lead=_lead(),
        enrichment_context={"verified": True},
    )
    store.create(run)
    evaluator = Evaluator()
    recovered = WorkflowOrchestrator(evaluator, store).recover_stalled(
        RecoveryRequest(owner="recovery-worker", lease_ttl_seconds=30)
    )
    assert len(recovered) == 1
    assert recovered[0].status == WorkflowRunStatus.READY_FOR_EXECUTION
    assert recovered[0].recovery_attempts == 1
    assert evaluator.calls == 1


def test_execution_claim_prevents_parallel_executor_and_completion_is_idempotent():
    store = InMemoryWorkflowRunStore()
    evaluator = Evaluator()
    engine = WorkflowOrchestrator(evaluator, store)
    run = engine.start(StartLeadWorkflowRequest(lead=_lead())).run
    claimed = engine.claim_execution(run.run_id, ExecutionClaimRequest(owner="n8n-a", ttl_seconds=60))
    assert claimed.execution_claim is not None

    with pytest.raises(ValueError, match="already leased"):
        engine.claim_execution(run.run_id, ExecutionClaimRequest(owner="n8n-b", ttl_seconds=60))

    with pytest.raises(ValueError, match="does not match"):
        engine.complete_execution(run.run_id, ExecutionReceipt(executor="n8n-a", claim_id="wrong"))

    receipt = ExecutionReceipt(
        executor="n8n-a",
        claim_id=claimed.execution_claim.claim_id,
        external_refs={"crm": "123"},
    )
    completed = engine.complete_execution(run.run_id, receipt)
    repeated = engine.complete_execution(run.run_id, receipt)
    assert completed.status == WorkflowRunStatus.COMPLETED
    assert repeated == completed
