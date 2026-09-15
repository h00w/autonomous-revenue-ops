# Phase 4 completion gates

Phase 4 is contract-complete when:

- workflow runs have explicit typed lifecycle states and history;
- workflow starts are idempotent and replay does not repeat AI evaluation;
- HUMAN_REVIEW stops before execution and requires explicit identified approval;
- RESEARCH_MORE can resume with new evidence;
- BLOCK completes without execution authorization;
- authorized runs require an execution receipt before completion;
- REST endpoints expose start/get/approve/resume/complete contracts;
- n8n reference workflow forwards correlation and idempotency identifiers;
- workflow smoke harness performs no HTTP request without `--execute`;
- existing Phase 0-3 regression/evaluation gates remain green.

The completion claim is **workflow-contract complete**, not durable-orchestration validated. Durable persistence, restart recovery, distributed locking, retries, circuit breakers, DLQ and inbound authentication remain later controls.
