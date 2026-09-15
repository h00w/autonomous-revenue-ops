# Phase 5 Completion Gates

Phase 5 is complete when the repository demonstrates restart-safe single-host workflow durability, bounded failure recovery, authenticated replay-resistant ingress, and regression safety without overstating distributed or live-provider validation.

## Verified gates

- [x] Phase 0–4 regression suite remains green.
- [x] SQLite workflow state survives store reopen/process restart boundaries.
- [x] workflow idempotency is enforced by a database unique constraint.
- [x] stale writers are rejected by optimistic revision checks.
- [x] executor/recovery leases prevent concurrent ownership and expire predictably.
- [x] persisted `RUNNING` workflows can be recovered under an explicit worker lease.
- [x] human-review/research wait states are not automatically replayed.
- [x] identical execution completion receipts are idempotent.
- [x] conflicting completion receipts are rejected.
- [x] retry behavior is bounded and limited to normalized retryable integration failures.
- [x] non-retryable/exhausted integration failures can be persisted to a DLQ.
- [x] circuit breakers open at a configured threshold and recover after the timeout.
- [x] signed webhooks verify timestamp + exact raw body with HMAC-SHA256.
- [x] stale, tampered, and replayed webhook requests are rejected.
- [x] replay protection persists across process restarts through SQLite.
- [x] production workflow API configuration fails closed when API authentication is missing.
- [x] production readiness exposes missing workflow-auth/webhook-signing controls.
- [x] reliability/security smoke harness performs zero network calls.
- [x] full CI test suite: **78/78 passed**.
- [x] deterministic policy benchmark: **6/6 passed (100%)**.

## CI smoke evidence

The final Phase 5 PR gate also preserved prior evidence:

- HubSpot dry-run — no external call.
- Salesforce dry-run — no external call.
- Slack dry-run — no external call.
- SMTP dry-run — no external call.
- OpenAI dry-run — no external call.
- Anthropic dry-run — no external call.
- Gemini dry-run — no external call.
- workflow smoke — no HTTP request.
- reliability/security smoke — `network_calls: 0`, injected retry recovered on attempt 2.

## Evidence boundary

SQLite establishes transactional, restart-safe durability for a single host. This phase does **not** claim horizontally scaled database coordination, multi-region HA, disaster recovery, or live external-provider validation. Those claims require later deployment/live-capability evidence.

AI evaluation remains at-least-once across a crash that occurs after a `RUNNING` checkpoint. External side effects are separately guarded by deterministic authorization, execution claims/leases, provider-side references/idempotency where available, and explicit completion receipts.
