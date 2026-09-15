# ADR-002: Prove Idempotency Semantics Before Adding Durable Storage

- **Status:** Accepted
- **Date:** 2026-09-15

## Context

Revenue operations workflows can create consequential side effects such as CRM records, assignments and outreach. Retries from clients or workflow engines must not duplicate those actions. Phase 1 needs executable idempotency semantics, but durable distributed infrastructure belongs to later reliability/deployment phases.

## Decision

Define idempotency as a first-class service concern now, using:

- an explicit `Idempotency-Key` request header when supplied;
- a deterministic SHA-256-derived key when no client key is provided;
- a thread-safe TTL-backed in-memory implementation behind an isolated module;
- replay behavior that returns the original logical event with `replayed=true`.

## Consequences

### Positive

- duplicate-suppression behavior is testable immediately;
- later Redis/Postgres storage can replace the implementation without changing the API contract;
- event IDs remain stable across retries of the same logical operation.

### Limitations

- state is lost on process restart;
- separate replicas do not share duplicate state;
- the implementation is not sufficient for multi-instance production deployment.

A shared durable store is a mandatory gate in the later reliability/deployment phases.
