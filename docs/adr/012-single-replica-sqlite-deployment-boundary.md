# ADR-012: Keep the SQLite deployment single-replica

## Status
Accepted for Phase 8.

## Context
The current workflow store uses SQLite WAL mode and provides restart-safe single-host durability, optimistic revisions, leases and idempotency. That evidence does not establish safe horizontal application replication across independently scheduled pods and storage topologies.

## Decision
The reference Kubernetes deployment uses exactly one application replica, `Recreate` strategy and a `ReadWriteOnce` volume. Production readiness fails closed when SQLite is configured with more than one application replica.

## Consequences
The reference topology can survive process/pod restart when its persistent volume survives, but it does not provide application-level high availability. Horizontal scaling is deferred until the workflow/idempotency/replay state is moved to a shared transactional backend and validated under concurrency/failover tests.
