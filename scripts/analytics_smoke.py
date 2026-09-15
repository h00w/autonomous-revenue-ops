"""Phase 7 local analytics smoke. Uses synthetic in-memory runs and makes no network calls."""

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.analytics.models import BusinessImpactScenario  # noqa: E402
from src.analytics.service import AnalyticsService  # noqa: E402
from src.models import LeadInput  # noqa: E402
from src.orchestration.models import WorkflowRun, WorkflowRunStatus  # noqa: E402
from src.orchestration.store import InMemoryWorkflowRunStore  # noqa: E402


def main() -> None:
    store = InMemoryWorkflowRunStore()
    now = datetime.now(timezone.utc)
    for index, status in enumerate([WorkflowRunStatus.COMPLETED, WorkflowRunStatus.FAILED], start=1):
        run = WorkflowRun(
            run_id=f"synthetic_{index}",
            correlation_id=f"corr_synthetic_{index}",
            idempotency_key=f"idem_synthetic_{index}",
            status=status,
            lead=LeadInput(
                lead_id=f"synthetic_lead_{index}",
                name="Synthetic Lead",
                email=f"synthetic{index}@example.com",
                company="Synthetic Company",
            ),
            created_at=now,
            updated_at=now + timedelta(seconds=index),
        )
        store.create(run)
    service = AnalyticsService(store)
    snapshot = service.snapshot()
    projection = service.project_business_impact(
        BusinessImpactScenario(
            workflows_per_month=1000,
            manual_minutes_per_workflow=10,
            automation_rate=0.8,
            loaded_hourly_cost=50,
            automation_cost_per_automated_workflow=0.05,
            currency="USD",
        )
    )
    print(json.dumps({
        "status": "synthetic-smoke",
        "network_calls": 0,
        "runtime_evidence_class": snapshot.evidence_class,
        "runtime_source_runs": snapshot.source_run_count,
        "projection_evidence_class": projection.evidence_class,
        "projection_is_measured_roi": False,
    }))


if __name__ == "__main__":
    main()
