from collections import deque

from fastapi.testclient import TestClient

from src.ai.models import ResearchOutput, SupervisedLeadResult
from src.api import create_app
from src.models import Decision, LeadInput, PolicyResult, Qualification
from src.orchestration.engine import WorkflowOrchestrator
from src.orchestration.store import InMemoryWorkflowRunStore
import src.orchestration.api as orchestration_api


class Evaluator:
    def __init__(self):
        self.calls = 0

    def evaluate(self, lead, *, enrichment_context=None, correlation_id=None):
        self.calls += 1
        return SupervisedLeadResult(
            lead=lead,
            research=ResearchOutput(
                summary="Synthetic",
                evidence=["evidence"],
                open_questions=[],
                risk_flags=[],
                confidence=0.9,
            ),
            qualification=Qualification(
                score=90,
                confidence=0.92,
                icp_fit=90,
                intent=90,
                urgency=70,
                risk_flags=[],
                evidence=["evidence"],
            ),
            qualification_rationale="Synthetic",
            policy=PolicyResult(
                decision=Decision.AUTO_ROUTE,
                authorized_for_outreach=True,
                reason="Synthetic",
                next_action="Synthetic",
            ),
            outreach=None,
            traces=[],
        )


def payload():
    return {
        "lead": {
            "lead_id": "api_phase4",
            "name": "API Test",
            "email": "api@example.com",
            "company": "Test AB",
            "consent_to_contact": True
        },
        "enrichment_context": {}
    }


def test_workflow_api_start_replay_get_and_complete(monkeypatch):
    evaluator = Evaluator()
    engine = WorkflowOrchestrator(evaluator, InMemoryWorkflowRunStore())
    monkeypatch.setattr(orchestration_api, "get_workflow_orchestrator", lambda: engine)
    client = TestClient(create_app())

    first = client.post(
        "/v1/workflows/leads",
        headers={"Idempotency-Key": "api-key", "X-Correlation-ID": "corr-api"},
        json=payload(),
    )
    assert first.status_code == 200
    body = first.json()
    run_id = body["run"]["run_id"]
    assert body["replayed"] is False
    assert body["run"]["correlation_id"] == "corr-api"
    assert body["run"]["status"] == "READY_FOR_EXECUTION"

    replay = client.post("/v1/workflows/leads", headers={"Idempotency-Key": "api-key"}, json=payload())
    assert replay.status_code == 200
    assert replay.json()["replayed"] is True
    assert replay.json()["run"]["run_id"] == run_id
    assert evaluator.calls == 1

    fetched = client.get(f"/v1/workflows/runs/{run_id}")
    assert fetched.status_code == 200

    completed = client.post(
        f"/v1/workflows/runs/{run_id}/complete",
        json={"executor": "n8n", "external_refs": {"crm": "record-1"}},
    )
    assert completed.status_code == 200
    assert completed.json()["status"] == "COMPLETED"


def test_workflow_api_returns_404_for_unknown_run(monkeypatch):
    engine = WorkflowOrchestrator(Evaluator(), InMemoryWorkflowRunStore())
    monkeypatch.setattr(orchestration_api, "get_workflow_orchestrator", lambda: engine)
    client = TestClient(create_app())
    response = client.get("/v1/workflows/runs/run_missing")
    assert response.status_code == 404
