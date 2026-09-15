# ADR-004: Normalize Integration Errors Before Adding Automatic Retries

- **Status:** Accepted
- **Date:** 2026-09-15

## Context

External providers expose incompatible exception classes, HTTP payloads, rate-limit headers and failure semantics. Adding retry loops directly inside each provider adapter would duplicate logic and risks retrying non-idempotent or permanent failures.

## Decision

Phase 2 adapters normalize failures into `IntegrationError` with:

- provider;
- normalized error kind;
- retryable classification;
- HTTP status where available;
- parsed `Retry-After` seconds where available;
- provider diagnostic detail.

No automatic retry loop is added in Phase 2. Phase 5 will consume the normalized metadata and apply centralized retry budgets, exponential backoff, jitter, circuit breaking and DLQ/replay policy.

## Consequences

### Positive

- provider-specific transport concerns do not leak into workflow logic;
- retry policy can be tested once across integrations;
- permanent failures cannot accidentally enter an infinite retry loop;
- rate-limit evidence is retained for later scheduling.

### Trade-offs

- transient provider failures currently return immediately to the caller;
- end-to-end workflow recovery remains incomplete until Phase 5.
