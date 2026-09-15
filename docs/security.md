# Security Controls

## Signed inbound webhooks

`POST /v1/webhooks/lead` requires:

- `X-ARO-Timestamp`
- `X-ARO-Signature: sha256=<hex>`

The signature covers `timestamp + '.' + raw_request_body` using HMAC-SHA256. Verification uses constant-time comparison, rejects timestamps outside the configured skew window, and records the signature fingerprint in SQLite so a valid captured request cannot be replayed inside the acceptance window.

The signature is verified before JSON parsing or workflow execution.

## Workflow API authentication

When `ARO_WORKFLOW_API_KEY` is configured, workflow endpoints require `X-ARO-API-Key`. In `production`, missing authentication configuration fails closed with HTTP 503 rather than silently exposing mutation endpoints.

## Execution authorization

Security is layered:

1. model output is typed and locally validated;
2. deterministic policy authorizes or blocks action;
3. human approval is separate evidence when required;
4. an authorized executor must acquire a lease/claim before side effects;
5. completion is recorded with an execution receipt.

No LLM prompt can mint workflow API credentials, webhook signatures, execution claims, or policy authorization.

## Secrets

Secrets remain environment/secret-manager inputs represented by `SecretStr`. Example files contain empty values only. Logs and DLQ payloads must contain operational identifiers rather than credentials or raw secret material.
