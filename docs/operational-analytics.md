# Operational Analytics & Observability

Phase 7 derives operational evidence directly from the durable `WorkflowRunStore`. There is no separate analytics database with an independent interpretation of workflow truth.

## Measured runtime snapshot

`GET /v1/analytics/summary` returns `evidence_class=measured_runtime` and aggregates persisted runs into:

- workflow status counts;
- deterministic policy decision counts;
- completion/failure ratios;
- human-review and additional-research ratios;
- authorization ratio;
- recovery ratio;
- execution-receipt ratio;
- average and p95 recorded workflow lifecycle duration.

The metrics are aggregate and do not expose lead IDs, names, email addresses, messages, enrichment payloads, prompt bodies, or credentials.

## Prometheus-compatible surface

`GET /v1/analytics/metrics` renders aggregate text metrics suitable for scraping or forwarding into a monitoring system. The endpoint uses the same workflow API authentication control as other operational endpoints.

## Important timing semantics

`recorded_lifecycle_seconds` is `updated_at - created_at` for the persisted run. For a completed/failed run it describes the recorded workflow lifecycle. For a waiting/in-progress run it describes time to the latest persisted transition, not wall-clock age and not end-to-end customer latency.

## Export

`python scripts/analytics_report.py --output runtime-analytics.json` exports the aggregate measured-runtime snapshot from the configured workflow store without requiring AI provider credentials.
