# Phase 4 workflow orchestration

Phase 4 wraps the Phase 3 governed supervisor in an explicit workflow state machine. It does not move business authorization into n8n or into an LLM.

```text
RECEIVED
   |
RUNNING
   |
   +-- HUMAN_REVIEW --> WAITING_HUMAN_REVIEW -- approve --> READY_FOR_EXECUTION
   |                                             reject --> COMPLETED
   |
   +-- RESEARCH_MORE -> WAITING_RESEARCH -- new evidence --> RUNNING
   |
   +-- BLOCK --------> COMPLETED
   |
   +-- AUTO_ROUTE/NURTURE ----------------------> READY_FOR_EXECUTION
                                                    |
                                               execution receipt
                                                    |
                                                COMPLETED
```

## Idempotency

A workflow start uses the caller's `Idempotency-Key` when supplied. Otherwise a deterministic key is derived from the typed lead/enrichment request. Repeating the same key returns the original run and does not re-run AI evaluation.

## Authorization

`execution_authorized` is true only when the deterministic policy already authorizes the path or when the deterministic policy explicitly required `HUMAN_REVIEW` and an identified reviewer subsequently approved it. Human approval is stored separately; the original `PolicyResult` is never rewritten to make it appear that the model or policy made a different decision.

## Persistence boundary

Phase 4 intentionally uses `InMemoryWorkflowRunStore`, isolated behind `WorkflowRunStore`. This proves run semantics and API contracts but is not a durable production store. Phase 5/8 must replace or back it with durable persistence and add restart recovery, leasing/concurrency controls, retry policy, DLQ and operational retention.

## External execution boundary

The Phase 4 engine does not directly call HubSpot, Salesforce, Slack or SMTP. An authorized run enters `READY_FOR_EXECUTION`. A bounded executor such as n8n performs approved effects and posts an `ExecutionReceipt` to `/v1/workflows/runs/{run_id}/complete`. This keeps side effects outside AI reasoning and makes completion explicit rather than inferred.
