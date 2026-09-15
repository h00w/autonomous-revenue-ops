from uuid import uuid4

from fastapi.testclient import TestClient

from src.api import app

client = TestClient(app)


def payload() -> dict:
    return {
        "lead": {
            "lead_id": "lead_api",
            "name": "Grace Example",
            "email": "grace@example.com",
            "company": "Example SaaS",
            "role": "COO",
            "source": "website",
            "message": "Need workflow automation",
            "consent_to_contact": True,
        },
        "qualification": {
            "score": 89,
            "confidence": 0.92,
            "icp_fit": 90,
            "intent": 88,
            "urgency": 71,
            "risk_flags": [],
            "evidence": ["Synthetic API test evidence"],
        },
    }


def test_liveness_endpoint():
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_readiness_endpoint_exposes_checks():
    response = client.get("/health/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["checks"]["policy_engine"] == "ok"
    assert body["checks"]["idempotency_store"] == "ok"


def test_evaluate_endpoint_returns_governed_result_and_correlation_id():
    correlation_id = f"corr_{uuid4().hex}"
    idempotency_key = f"idem_{uuid4().hex}"
    response = client.post(
        "/v1/leads/evaluate",
        json=payload(),
        headers={
            "X-Correlation-ID": correlation_id,
            "Idempotency-Key": idempotency_key,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert response.headers["X-Correlation-ID"] == correlation_id
    assert body["event"]["correlation_id"] == correlation_id
    assert body["event"]["idempotency_key"] == idempotency_key
    assert body["policy"]["decision"] == "AUTO_ROUTE"
    assert body["replayed"] is False


def test_same_idempotency_key_replays_original_event():
    idempotency_key = f"idem_{uuid4().hex}"
    headers = {
        "X-Correlation-ID": f"corr_{uuid4().hex}",
        "Idempotency-Key": idempotency_key,
    }
    first = client.post("/v1/leads/evaluate", json=payload(), headers=headers)
    second = client.post("/v1/leads/evaluate", json=payload(), headers=headers)

    assert first.status_code == second.status_code == 200
    assert first.json()["event"]["event_id"] == second.json()["event"]["event_id"]
    assert first.json()["replayed"] is False
    assert second.json()["replayed"] is True


def test_invalid_lead_is_rejected_before_policy_execution():
    invalid = payload()
    invalid["lead"]["email"] = "not-an-email"
    response = client.post("/v1/leads/evaluate", json=invalid)
    assert response.status_code == 422
