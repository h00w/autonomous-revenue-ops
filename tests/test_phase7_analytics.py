from datetime import datetime, timedelta, timezone

import pytest

from src.ai.models import ResearchOutput, SupervisedLeadResult
from src.analytics.models import BusinessImpactScenario
from src.analytics.prometheus import render_prometheus
from src.analytics.service import AnalyticsService
from src.models import Decision, LeadInput, PolicyResult, Qualification
from src.orchestration.models import ExecutionReceipt, WorkflowRun, WorkflowRunStatus
from src.orchestration.store import InMemoryWorkflowRunStore, SQLiteWorkflowRunStore


def _lead(index: int) -> LeadInput:
    return LeadInput(
        lead_id=f"lead_{index}",
        name=f"Person {index}",
        email=f"person{index}@example.com",
        company="Example Company",
        consent_to_contact=True,
    )


def _result(lead: LeadInput, decision: Decision, authorized: bool) -> SupervisedLeadResult:
    qualification = Qualification(score=90 if decision == Decision.AUTO_ROUTE else 70, confidence=0.9, icp_fit=80, intent=80, urgency=60, risk_flags=[])
    return SupervisedLeadResult(
        lead=lead,
        research=ResearchOutput(summary="synthetic test research", evidence=["synthetic"], open_questions=[], risk_flags=[], confidence=0.9),
        qualification=qualification,
        qualification_rationale="synthetic",
        policy=PolicyResult(decision=decision, authorized_for_outreach=authorized, reason="synthetic", next_action="synthetic"),
    )


def _run(index: int, status: WorkflowRunStatus, decision: Decision, authorized: bool, seconds: int, *, recovered: bool = False, receipt: bool = False) -> WorkflowRun:
    lead = _lead(index)
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return WorkflowRun(
        run_id=f"run_{index}", correlation_id=f"corr_{index}", idempotency_key=f"idem_{index}", status=status, lead=lead,
        created_at=start, updated_at=start + timedelta(seconds=seconds), result=_result(lead, decision, authorized),
        execution_authorized=authorized, recovery_attempts=1 if recovered else 0,
        execution_receipt=ExecutionReceipt(executor="test") if receipt else None,
    )


def test_operational_snapshot_is_derived_from_persisted_runs():
    store = InMemoryWorkflowRunStore()
    fixtures = [
        _run(1, WorkflowRunStatus.COMPLETED, Decision.AUTO_ROUTE, True, 1, receipt=True),
        _run(2, WorkflowRunStatus.WAITING_HUMAN_REVIEW, Decision.HUMAN_REVIEW, False, 2),
        _run(3, WorkflowRunStatus.WAITING_RESEARCH, Decision.RESEARCH_MORE, False, 3),
        _run(4, WorkflowRunStatus.FAILED, Decision.AUTO_ROUTE, True, 4, recovered=True),
        _run(5, WorkflowRunStatus.COMPLETED, Decision.NURTURE, True, 5),
    ]
    for run in fixtures:
        store.create(run)
    snapshot = AnalyticsService(store).snapshot()
    assert snapshot.evidence_class == "measured_runtime"
    assert snapshot.source_run_count == 5
    assert snapshot.status_counts["COMPLETED"] == 2
    assert snapshot.status_counts["FAILED"] == 1
    assert snapshot.decision_counts["AUTO_ROUTE"] == 2
    assert snapshot.human_review_rate == pytest.approx(0.2)
    assert snapshot.research_more_rate == pytest.approx(0.2)
    assert snapshot.authorization_rate == pytest.approx(0.6)
    assert snapshot.failure_rate == pytest.approx(0.2)
    assert snapshot.completion_rate == pytest.approx(0.4)
    assert snapshot.recovery_rate == pytest.approx(0.2)
    assert snapshot.execution_receipt_rate == pytest.approx(1 / 3)
    assert snapshot.average_recorded_lifecycle_seconds == pytest.approx(3.0)
    assert snapshot.p95_recorded_lifecycle_seconds == pytest.approx(5.0)


def test_sqlite_list_runs_supports_analytics_after_reopen(tmp_path):
    path = str(tmp_path / "runs.sqlite3")
    store = SQLiteWorkflowRunStore(path)
    store.create(_run(1, WorkflowRunStatus.COMPLETED, Decision.AUTO_ROUTE, True, 4, receipt=True))
    reopened = SQLiteWorkflowRunStore(path)
    snapshot = AnalyticsService(reopened).snapshot()
    assert snapshot.source_run_count == 1
    assert snapshot.completed_with_receipt_count == 1
    assert snapshot.decision_counts == {"AUTO_ROUTE": 1}


def test_business_impact_is_explicitly_scenario_projection():
    projection = AnalyticsService.project_business_impact(BusinessImpactScenario(
        workflows_per_month=1000, manual_minutes_per_workflow=10, automation_rate=0.8,
        loaded_hourly_cost=50, automation_cost_per_automated_workflow=0.05, currency="USD",
    ))
    assert projection.evidence_class == "scenario_projection"
    assert projection.automated_workflows == 800
    assert projection.manual_hours_baseline == 166.67
    assert projection.manual_hours_remaining == 33.33
    assert projection.hours_avoided == 133.33
    assert projection.capacity_value == 6666.67
    assert projection.automation_operating_cost == 40
    assert projection.net_capacity_value == 6626.67
    assert any("not measured customer ROI" in assumption for assumption in projection.assumptions)


def test_prometheus_output_is_aggregate_and_contains_no_lead_pii():
    store = InMemoryWorkflowRunStore()
    store.create(_run(1, WorkflowRunStatus.COMPLETED, Decision.AUTO_ROUTE, True, 2, receipt=True))
    metrics = render_prometheus(AnalyticsService(store).snapshot())
    assert "aro_workflow_runs 1" in metrics
    assert 'aro_policy_decision{decision="AUTO_ROUTE"} 1' in metrics
    assert "person1@example.com" not in metrics
    assert "lead_1" not in metrics
