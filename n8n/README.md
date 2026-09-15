# n8n Orchestration Surface

`lead-intake.workflow.json` is the importable visual orchestration entrypoint for the governed workflow.

```text
Inbound lead
   ↓
n8n Webhook
   ↓
Correlation + idempotency headers
   ↓
Autonomous Revenue Ops FastAPI
   ↓
Durable workflow state
   ↓
Research → Qualification → deterministic policy
   ↓
AUTO_ROUTE / NURTURE / HUMAN_REVIEW / RESEARCH_MORE / BLOCK
   ↓
Bounded execution + receipts + analytics
```

## Import

1. Create an n8n Cloud or self-hosted project.
2. Import `lead-intake.workflow.json`.
3. Set `ARO_API_BASE_URL` to the staging API base URL, or replace the expression with an n8n project variable.
4. For an authenticated staging API, configure a **Header Auth** credential in n8n with header `X-ARO-API-Key`. Attach the credential to the `Start Governed Workflow` HTTP Request node.
5. Keep the exported repository workflow credential-free. Never place API keys directly in the JSON export.
6. Activate only after the target API is a sandbox/staging environment approved for the demo.

## Public-demo recommendation

For recruiter/client proof, publish screenshots or a short screen recording of the workflow canvas and execution trace. Do not expose an editable n8n instance or live credentials publicly.

## What n8n does not own

n8n is the visual orchestration/integration layer. It does not own policy authority, durable business state, AI output validation, idempotency truth, or execution authorization. Those controls remain in the FastAPI service so the same governance applies regardless of trigger source.
