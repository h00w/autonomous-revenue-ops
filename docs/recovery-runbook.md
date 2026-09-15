# Recovery Runbook

## Stalled workflow after process restart

1. Confirm the API and SQLite workflow database are available.
2. Inspect the run with `GET /v1/workflows/runs/{run_id}`.
3. Only a persisted `RUNNING` run is eligible for automatic recovery.
4. Call `POST /v1/workflows/recover` with a unique worker identity.
5. Confirm `recovery_attempts` incremented and the run reached a governed terminal/wait/ready state.

## Dependency outage

Retry only normalized failures marked `retryable=true`. Respect provider `Retry-After` when present. When retry attempts are exhausted, persist an operationally safe payload to the DLQ. Do not place API keys, webhook secrets, access tokens, or unnecessary PII in DLQ payloads.

## Circuit open

An open circuit means repeated dependency failures crossed the configured threshold. Do not bypass it manually by adding unbounded retries. Restore the dependency, allow the recovery timeout to pass, then execute a controlled smoke/canary operation.

## Execution ambiguity

If it is unclear whether a CRM/email side effect occurred, do not create a second claim blindly. Inspect the existing execution claim and provider-side idempotency/reference information. Reconcile first, then either complete with the original receipt/reference or explicitly release/recover through an operator-controlled procedure.

## Webhook rejection

A 401 from the webhook route indicates missing/invalid signature headers, stale timestamp, signature mismatch, or replay. Never disable verification to clear the incident; rotate/reconcile the shared secret and sender clock/configuration instead.
