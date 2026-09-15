# n8n orchestration contract

The repository includes `n8n/lead-intake.workflow.json` as an importable reference workflow. It uses n8n's Webhook, HTTP Request, and Respond to Webhook nodes to forward a typed lead request to the Autonomous Revenue Ops API. Current n8n documentation supports using the HTTP Request node for API calls and mapping prior-node data with expressions.

Set `ARO_API_BASE_URL` in the n8n runtime to the API base URL. The template forwards both `Idempotency-Key` and `X-Correlation-ID`, using incoming values when available and the n8n execution ID as a fallback.

## API endpoints

- `POST /v1/workflows/leads` — start or replay a workflow.
- `GET /v1/workflows/runs/{run_id}` — inspect current state and history.
- `POST /v1/workflows/runs/{run_id}/approval` — record a human approval/rejection.
- `POST /v1/workflows/runs/{run_id}/resume-research` — supply additional evidence and re-evaluate.
- `POST /v1/workflows/runs/{run_id}/complete` — record bounded external execution results.

The reference workflow is intentionally inactive and carries no credentials. Authentication/signature validation for inbound webhooks is a Phase 5 security control; do not expose an unauthenticated production endpoint before that phase is implemented.
