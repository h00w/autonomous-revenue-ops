from .models import OperationalSnapshot


def render_prometheus(snapshot: OperationalSnapshot) -> str:
    """Render aggregate workflow telemetry only; no lead/customer identifiers are emitted."""
    lines = [
        "# HELP aro_workflow_runs Number of persisted workflow runs.",
        "# TYPE aro_workflow_runs gauge",
        f"aro_workflow_runs {snapshot.source_run_count}",
    ]
    for status, count in sorted(snapshot.status_counts.items()):
        lines.append(f'aro_workflow_status{{status="{status}"}} {count}')
    for decision, count in sorted(snapshot.decision_counts.items()):
        lines.append(f'aro_policy_decision{{decision="{decision}"}} {count}')
    gauges = {
        "aro_workflow_completion_ratio": snapshot.completion_rate,
        "aro_workflow_failure_ratio": snapshot.failure_rate,
        "aro_workflow_human_review_ratio": snapshot.human_review_rate,
        "aro_workflow_research_more_ratio": snapshot.research_more_rate,
        "aro_workflow_authorization_ratio": snapshot.authorization_rate,
        "aro_workflow_recovery_ratio": snapshot.recovery_rate,
        "aro_execution_receipt_ratio": snapshot.execution_receipt_rate,
        "aro_workflow_lifecycle_seconds_avg": snapshot.average_recorded_lifecycle_seconds,
        "aro_workflow_lifecycle_seconds_p95": snapshot.p95_recorded_lifecycle_seconds,
    }
    lines.extend(f"{name} {value}" for name, value in gauges.items())
    return "\n".join(lines) + "\n"
