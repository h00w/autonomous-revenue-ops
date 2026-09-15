from collections import Counter
from math import ceil

from ..models import Decision
from ..orchestration.models import WorkflowRunStatus
from ..orchestration.store import WorkflowRunStore
from .models import BusinessImpactProjection, BusinessImpactScenario, OperationalSnapshot


class AnalyticsService:
    """Derive aggregate operational evidence from the workflow source of truth."""

    def __init__(self, store: WorkflowRunStore) -> None:
        self.store = store

    def snapshot(self) -> OperationalSnapshot:
        runs = self.store.list_runs()
        total = len(runs)
        statuses = Counter(run.status.value for run in runs)
        decisions = Counter(
            run.result.policy.decision.value
            for run in runs
            if run.result is not None
        )
        authorized = sum(1 for run in runs if run.execution_authorized)
        with_receipt = sum(1 for run in runs if run.execution_receipt is not None)
        recovered = sum(1 for run in runs if run.recovery_attempts > 0)
        durations = sorted(
            max((run.updated_at - run.created_at).total_seconds(), 0.0)
            for run in runs
        )

        def rate(value: int, denominator: int = total) -> float:
            return value / denominator if denominator else 0.0

        average = sum(durations) / len(durations) if durations else 0.0
        p95 = durations[max(ceil(0.95 * len(durations)) - 1, 0)] if durations else 0.0
        return OperationalSnapshot(
            source_run_count=total,
            status_counts=dict(sorted(statuses.items())),
            decision_counts=dict(sorted(decisions.items())),
            authorized_run_count=authorized,
            completed_with_receipt_count=with_receipt,
            recovered_run_count=recovered,
            completion_rate=rate(statuses[WorkflowRunStatus.COMPLETED.value]),
            failure_rate=rate(statuses[WorkflowRunStatus.FAILED.value]),
            human_review_rate=rate(decisions[Decision.HUMAN_REVIEW.value]),
            research_more_rate=rate(decisions[Decision.RESEARCH_MORE.value]),
            authorization_rate=rate(authorized),
            recovery_rate=rate(recovered),
            execution_receipt_rate=rate(with_receipt, authorized),
            average_recorded_lifecycle_seconds=average,
            p95_recorded_lifecycle_seconds=p95,
        )

    @staticmethod
    def project_business_impact(scenario: BusinessImpactScenario) -> BusinessImpactProjection:
        automated = scenario.workflows_per_month * scenario.automation_rate
        remaining = scenario.workflows_per_month - automated
        baseline_hours = scenario.workflows_per_month * scenario.manual_minutes_per_workflow / 60.0
        remaining_hours = remaining * scenario.manual_minutes_per_workflow / 60.0
        hours_avoided = baseline_hours - remaining_hours
        capacity_value = hours_avoided * scenario.loaded_hourly_cost
        automation_cost = automated * scenario.automation_cost_per_automated_workflow
        net_capacity_value = capacity_value - automation_cost

        def rounded(value: float) -> float:
            return round(value, 2)

        return BusinessImpactProjection(
            currency=scenario.currency,
            workflows_per_month=scenario.workflows_per_month,
            automated_workflows=rounded(automated),
            manual_workflows_remaining=rounded(remaining),
            manual_hours_baseline=rounded(baseline_hours),
            manual_hours_remaining=rounded(remaining_hours),
            hours_avoided=rounded(hours_avoided),
            capacity_value=rounded(capacity_value),
            automation_operating_cost=rounded(automation_cost),
            net_capacity_value=rounded(net_capacity_value),
            assumptions=[
                "Scenario projection only; values are not measured customer ROI.",
                "Each automated workflow is assumed to avoid the configured manual minutes.",
                "Loaded hourly cost and automation cost are user-supplied assumptions.",
                "No revenue uplift, opportunity cost, tax, discounting, or implementation cost is inferred.",
            ],
        )
