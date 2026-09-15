from collections import deque

from src.ai.models import QualificationRecommendation, ResearchOutput, SupervisedLeadResult
from src.models import Decision, LeadInput, PolicyResult
from src.orchestration.engine import WorkflowOrchestrator
from src.orchestration.models import (
    ExecutionReceipt,
    HumanApproval,
    ResearchResumeRequest,
    StartLeadWorkflowRequest,
    WorkflowRunStatus,
)
from src.orchestration.store import InMemoryWorkflowRunStore


class QueueEvaluator:
    def __init__(self, results):
        self.results = deque(results)
        self.calls = 0

    def evaluate(self, lead, *, enrichment_context=None, correlation_id=None):
        self.calls += 1
        item = self.results.popleft()
        if isinstance(item, Exception):
            raise item
        return item


def lead() -> LeadInput:
    return LeadInput(
        lead_id="lead_phase4",
        name="Grace Hopper",
        email="grace@example.com",
        company="Compiler Systems AB",
        role="CTO",
        message="Interested in governed automation",
        consent_to_contact=True,
    )


def result(decision: Decision, authorized: bool) -> SupervisedLeadResult:
    l = lead()
    qualification = QualificationRecommendation(
        score=85 if decision == Decision.AUTO_ROUTE else 70,
        confidence=0.9 if decision != Decision.RESEARCH_MORE else 0.5,
        icp_fit=80,
        intent=80,
        urgency=60,
        risk_flags=["needs_review"] if decision == Decision.HUMAN_REVIEW else [],
        evidence=["synthetic evidence"],
        rationale="Synthetic orchestration fixture.",
    ).to_domain()
    return SupervisedLeadResult(
        lead=l,
        research=ResearchOutput(
            summary="Synthetic research",
            evidence=["synthetic evidence"],
            open_questions=[],
            risk_flags=[],
            confidence=0.9,
        ),
        qualification=qualification,
        qualification_rationale="Synthetic orchestration fixture.",
        policy=PolicyResult(
            decision=decision,
            authorized_for_outreach=authorized,
            reason="Synthetic policy result.",
            next_action="Synthetic next action.",
        ),
        outreach=None,
        traces=[],
    )


def test_start_is_idempotent_and_does_not_repeat_ai_evaluation():
    evaluator = QueueEvaluator([result(Decision.AUTO_ROUTE, True)])
    engine = WorkflowOrchestrator(evaluator, InMemoryWorkflowRunStore())
    body = StartLeadWorkflowRequest(lead=lead())

    first = engine.start(body, correlation_id="corr_1", idempotency_key="same-key")
    second = engine.start(body, correlation_id="corr_2", idempotency_key="same-key")

    assert first.replayed is False
    assert second.replayed is True
    assert first.run.run_id == second.run.run_id
    assert second.run.correlation_id == "corr_1"
    assert evaluator.calls == 1
    assert first.run.status == WorkflowRunStatus.READY_FOR_EXECUTION
    assert first.run.execution_authorized is True


def test_human_review_requires_explicit_approval_before_execution():
    evaluator = QueueEvaluator([result(Decision.HUMAN_REVIEW, False)])
    engine = WorkflowOrchestrator(evaluator, InMemoryWorkflowRunStore())
    run = engine.start(StartLeadWorkflowRequest(lead=lead())).run
    assert run.status == WorkflowRunStatus.WAITING_HUMAN_REVIEW
    assert run.execution_authorized is False

    approved = engine.approve(
        run.run_id,
        HumanApproval(approved=True, reviewer="revops@example.com", note="Verified manually"),
    )
    assert approved.status == WorkflowRunStatus.READY_FOR_EXECUTION
    assert approved.execution_authorized is True
    assert approved.result.policy.authorized_for_outreach is False


def test_research_resume_reruns_evaluation_and_can_become_ready():
    evaluator = QueueEvaluator([
        result(Decision.RESEARCH_MORE, False),
        result(Decision.AUTO_ROUTE, True),
    ])
    engine = WorkflowOrchestrator(evaluator, InMemoryWorkflowRunStore())
    run = engine.start(StartLeadWorkflowRequest(lead=lead())).run
    assert run.status == WorkflowRunStatus.WAITING_RESEARCH

    resumed = engine.resume_research(
        run.run_id,
        ResearchResumeRequest(enrichment_context={"verified_budget": True}),
    )
    assert resumed.status == WorkflowRunStatus.READY_FOR_EXECUTION
    assert resumed.execution_authorized is True
    assert evaluator.calls == 2


def test_completion_requires_ready_and_authorized_state():
    evaluator = QueueEvaluator([result(Decision.AUTO_ROUTE, True)])
    engine = WorkflowOrchestrator(evaluator, InMemoryWorkflowRunStore())
    run = engine.start(StartLeadWorkflowRequest(lead=lead())).run
    completed = engine.complete_execution(
        run.run_id,
        ExecutionReceipt(executor="n8n", external_refs={"crm": "123"}),
    )
    assert completed.status == WorkflowRunStatus.COMPLETED
    assert completed.execution_receipt.external_refs["crm"] == "123"


def test_evaluator_failure_is_persisted_as_failed_run():
    evaluator = QueueEvaluator([RuntimeError("synthetic failure")])
    engine = WorkflowOrchestrator(evaluator, InMemoryWorkflowRunStore())
    run = engine.start(StartLeadWorkflowRequest(lead=lead())).run
    assert run.status == WorkflowRunStatus.FAILED
    assert run.error["type"] == "RuntimeError"
    assert "synthetic failure" in run.error["message"]
