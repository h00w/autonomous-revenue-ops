import argparse
import json
import sys

import httpx


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 4 workflow orchestration smoke check")
    parser.add_argument("--execute", action="store_true", help="POST one synthetic lead to a running API")
    parser.add_argument("--api-base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()

    payload = {
        "lead": {
            "lead_id": "smoke_phase4",
            "name": "Workflow Smoke",
            "email": "workflow-smoke@example.com",
            "company": "Synthetic Test Company",
            "source": "phase4-smoke",
            "message": "Synthetic orchestration capability check",
            "consent_to_contact": False,
        },
        "enrichment_context": {},
    }

    if not args.execute:
        print(json.dumps({
            "status": "dry-run",
            "endpoint": "/v1/workflows/leads",
            "payload_valid": True,
            "message": "No HTTP request made. Use --execute only against a configured local/test API.",
        }))
        return

    response = httpx.post(
        args.api_base_url.rstrip("/") + "/v1/workflows/leads",
        headers={"Idempotency-Key": "phase4-smoke-fixed-key"},
        json=payload,
        timeout=30.0,
    )
    response.raise_for_status()
    data = response.json()
    print(json.dumps({
        "status": "success",
        "run_id": data["run"]["run_id"],
        "workflow_status": data["run"]["status"],
        "replayed": data["replayed"],
    }))


if __name__ == "__main__":
    sys.exit(main())
