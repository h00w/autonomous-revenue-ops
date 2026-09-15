# ADR-001: Separate the Production API from the Reviewer UI

- **Status:** Accepted
- **Date:** 2026-09-15

## Context

Phase 0 used a Gradio application as an interactive proof. A production workflow needs a stable machine-facing contract that is not coupled to UI rendering or session behavior.

## Decision

Keep root `app.py` as the Hugging Face/Gradio reviewer surface and introduce `src/api.py` as the FastAPI production boundary. Both reuse domain models and policy logic below the transport layer.

## Consequences

### Positive

- n8n, SaaS webhooks, workers and external clients can use a versioned HTTP contract;
- the reviewer UI can evolve without changing production API semantics;
- generated OpenAPI documentation becomes available automatically;
- policy code remains framework-independent and directly unit-testable.

### Trade-offs

- the repository has two entry points;
- dependencies include both Gradio and FastAPI;
- later deployment may package the reviewer UI and API as separate services.
