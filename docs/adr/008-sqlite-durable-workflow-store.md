# ADR-008: Use SQLite as the Phase 5 restart-safe workflow boundary

## Status
Accepted for Phase 5.

## Decision
Implement `SQLiteWorkflowRunStore` behind the existing `WorkflowRunStore` protocol. Enforce idempotency with a unique database constraint, stale-writer detection with revisions, and executor/recovery ownership with transactional leases.

## Rationale
Phase 4 deliberately kept state process-local. SQLite adds real restart persistence and transactional behavior without coupling the domain state machine to an infrastructure SDK. The protocol preserves a later path to PostgreSQL.

## Consequences
This provides single-host restart safety, not distributed HA. Multi-replica production deployment must move the same contract to a shared production database before claiming horizontally scaled durability.
