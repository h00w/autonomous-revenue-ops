# ADR-006: Controlled multi-model fallback

## Status
Accepted

## Decision
Provider order is configuration-driven. Fallback is allowed for retryable availability failures and invalid/schema-invalid model output. Authentication errors, refusals, and other non-retryable failures fail closed. Every attempt is recorded in the generation trace.

## Consequences
The system can tolerate bounded provider degradation without creating an unbounded agent loop. A fallback does not bypass local schema validation or deterministic authorization. Phase 5 will add retry/backoff and circuit breaking around the same normalized error contract.
