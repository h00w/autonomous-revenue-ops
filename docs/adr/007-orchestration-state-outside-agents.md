# ADR-007: Keep workflow state and side-effect completion outside agents

## Status
Accepted

## Decision
Workflow lifecycle state is owned by deterministic application code, not by an LLM prompt or n8n node memory. AI agents return typed recommendations. Deterministic policy selects the authorization path. The orchestration engine persists state transitions through a `WorkflowRunStore`, and bounded external executors report explicit completion receipts.

## Consequences
Agent/model changes cannot silently skip human-review or research checkpoints. n8n can be replaced without changing workflow semantics. The initial Phase 4 store is process-local and therefore cannot support restart recovery or multiple replicas; durable storage is deliberately deferred to the reliability/deployment phases.
