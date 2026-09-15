# Runtime Configuration

Phase 1 uses `pydantic-settings` so configuration is typed, environment-driven and independent of source-code changes.

## Variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `ARO_APP_NAME` | `Autonomous Revenue Ops` | service display name |
| `ARO_SERVICE_VERSION` | `0.1.0` | runtime/API version |
| `ARO_ENVIRONMENT` | `development` | `development`, `test`, `staging`, or `production` |
| `ARO_API_PREFIX` | `/v1` | versioned API prefix |
| `ARO_LOG_LEVEL` | `INFO` | application log threshold |
| `ARO_IDEMPOTENCY_TTL_SECONDS` | `3600` | local duplicate-suppression TTL |

Copy `.env.example` to `.env` for local development. Do not commit `.env`, tokens, OAuth credentials or provider secrets.

## Local API

```bash
cp .env.example .env
python -m pip install -r requirements.txt
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

Useful endpoints:

- `GET /health/live`
- `GET /health/ready`
- `POST /v1/leads/evaluate`
- `GET /docs` for generated OpenAPI/Swagger documentation

## Example request

```bash
curl -X POST http://localhost:8000/v1/leads/evaluate \
  -H 'Content-Type: application/json' \
  -H 'X-Correlation-ID: corr_demo_001' \
  -H 'Idempotency-Key: idem_demo_001' \
  -d '{
    "lead": {
      "lead_id": "lead_demo_001",
      "name": "Ada Example",
      "email": "ada@example.com",
      "company": "Example AB",
      "role": "VP Revenue",
      "source": "website",
      "message": "Need workflow automation",
      "consent_to_contact": true
    },
    "qualification": {
      "score": 88,
      "confidence": 0.93,
      "icp_fit": 91,
      "intent": 86,
      "urgency": 75,
      "risk_flags": [],
      "evidence": ["Synthetic example evidence"]
    }
  }'
```

## Environment policy

Phase 1 supports environment names but does not yet provision separate infrastructure. Phase 8 will formalize deployment-specific secret stores, durable databases, migration controls and promotion rules between development, staging and production.
