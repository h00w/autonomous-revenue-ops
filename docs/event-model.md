# Event, Correlation and Idempotency Model

## Goals

The event model makes every accepted workflow decision traceable and prepares the service for later queueing, replay, analytics and audit storage.

## Event envelope

Every completed lead evaluation emits the logical shape below:

```json
{
  "event_id": "evt_<uuid>",
  "event_type": "lead.evaluation.completed",
  "event_version": "1.0",
  "occurred_at": "2026-09-15T09:00:00Z",
  "correlation_id": "corr_<uuid>",
  "idempotency_key": "idem_<hash-or-client-key>",
  "source": "revenue-ops-api",
  "payload": {
    "lead_id": "lead_123",
    "source": "website",
    "decision": "AUTO_ROUTE",
    "authorized_for_outreach": true
  }
}
```

## Identifier semantics

### `event_id`
Unique identifier for one logical completed evaluation. An idempotent replay returns the original event ID because it is the same logical operation, not a new business action.

### `correlation_id`
Trace identifier for a request/workflow chain. The API accepts `X-Correlation-ID`; otherwise it generates one. Downstream adapters in later phases must forward it.

### `idempotency_key`
Uniquely identifies a business operation that must not be executed twice. Clients may send `Idempotency-Key`. When omitted, Phase 1 derives a deterministic SHA-256-based key from the canonical typed request.

## Replay semantics

For the active TTL:

```text
same idempotency key
        │
        ├─ first request ──> evaluate policy ──> store response
        │
        └─ repeat request ─> return stored response with replayed=true
```

The original event ID and original event correlation ID are retained. This makes duplicate suppression explicit and reconstructable.

## Versioning policy

`event_version` starts at `1.0`. Backward-incompatible payload changes require a major version increment. Additive optional fields may use a minor version increment if consumers remain compatible.

## Data minimization

The event envelope intentionally stores decision metadata rather than the full lead body in its payload. Full request state is available to the application during evaluation, but later durable audit/storage layers should separately define retention, access and PII policies.

## Phase 1 storage boundary

The idempotency store is in-memory with TTL. This proves semantics and test behavior but does not survive process restart or coordinate across replicas. A durable shared implementation is required before multi-instance production deployment.
