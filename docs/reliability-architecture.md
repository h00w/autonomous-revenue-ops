# Phase 5 Reliability Architecture

Phase 5 moves workflow coordination from a process-local proof to restart-safe, single-node durability while keeping the execution boundary explicit.

## Guarantees implemented

- SQLite persistence survives API process restarts.
- `idempotency_key` is a database unique constraint, not only an in-memory map.
- workflow saves use optimistic revisions and reject stale writers.
- executor/recovery leases serialize bounded work.
- only `RUNNING` runs are automatically recoverable; human-review and research waits remain paused.
- execution completion is idempotent for an identical receipt and rejects conflicting receipts.
- retry behavior is bounded and applies only to normalized retryable `IntegrationError`s.
- exhausted/non-retryable integration failures can be persisted to a SQLite DLQ.
- circuit breakers stop repeated calls to a failing dependency.

## Recovery semantics

A crash can occur after `RUNNING` is persisted but before evaluation finishes. On restart, an operator or scheduler calls `POST /v1/workflows/recover`. The recovery worker acquires a lease, increments `recovery_attempts`, re-runs the governed evaluation, persists the new state, and releases the lease.

AI evaluation is therefore at-least-once across a crash boundary. External side effects are separately protected by an execution claim and receipt so evaluation replay does not itself duplicate CRM/email work.

## Durability boundary

SQLite is evidence of restart safety on one host. It is not evidence of high availability, cross-region failover, or horizontally scaled write coordination. A later deployment phase can replace the `WorkflowRunStore` implementation with PostgreSQL without changing orchestrator semantics.
