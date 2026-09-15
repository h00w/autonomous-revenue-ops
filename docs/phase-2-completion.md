# Phase 2 Completion — Real SaaS & CRM Integrations

## Objective

Replace placeholder external boundaries with production-oriented provider adapters while preserving deterministic business policy and keeping CI independent from private credentials.

## Deliverables

| Deliverable | Evidence |
| --- | --- |
| Provider-neutral CRM contract | `src/integrations/crm/base.py` |
| Canonical CRM lead/result schemas | `src/integrations/models.py` |
| HubSpot CRM v3 adapter | `src/integrations/crm/hubspot.py` |
| Salesforce Lead REST adapter | `src/integrations/crm/salesforce.py` |
| Slack incoming-webhook adapter | `src/integrations/notifications/slack.py` |
| SMTP email adapter | `src/integrations/notifications/email.py` |
| Generic HTTPS webhook adapter | `src/integrations/notifications/webhook.py` |
| External failure normalization | `src/integrations/http.py`, `src/integrations/errors.py` |
| Environment/secret configuration | `src/config.py`, `.env.example` |
| Provider factories | `src/integrations/factory.py` |
| Canonical lead mapper | `src/integrations/mapping.py` |
| Live validation harness | `scripts/integration_smoke.py` |
| Contract regression tests | `tests/test_*adapter.py`, `tests/test_integration_*.py` |
| Integration architecture | `docs/integrations.md` |
| Field mapping | `docs/crm-field-mapping.md` |
| Contract specification | `docs/integration-contracts.md` |
| Architecture decisions | `docs/adr/003-*`, `docs/adr/004-*` |

## CI exit criteria

Phase 2 repository implementation is complete when CI demonstrates:

- Phase 0/1 regression tests remain green;
- HubSpot create, update and owner-update contracts pass;
- Salesforce create, update and owner-update contracts pass;
- Salesforce email lookup safely escapes SOQL literals;
- arbitrary custom CRM fields are dropped unless allow-listed;
- Slack webhook host restrictions and delivery contract pass;
- SMTP TLS/authentication/message contract passes;
- generic webhook event contract passes;
- 400/401/403/404/409/429/5xx/timeout failures normalize correctly;
- `Retry-After` metadata is preserved;
- secret values remain masked in settings representation;
- integration smoke harness is dry-run safe;
- policy benchmark remains green.

## External capability-validation gate

CI contract validation is not equivalent to a live provider account. A stronger evidence level is available through:

```bash
python scripts/integration_smoke.py hubspot --execute
python scripts/integration_smoke.py salesforce --execute
python scripts/integration_smoke.py slack --execute
python scripts/integration_smoke.py smtp --execute
```

These commands require dedicated sandbox/test credentials and create real external records/messages. Until that evidence is collected, the appropriate claim is:

> **Provider adapters implemented and contract-tested; live-account capability validation pending.**

A live-account validation can be added later without blocking architecture work in subsequent phases, but it remains a required evidence item before the final Production Validated claim in Phase 10.

## Deliberate Phase 2 boundaries

- no automatic retries/circuit breakers yet;
- no persistent DLQ/replay yet;
- no inbound webhook signature verification yet;
- no Gmail/Google Workspace OAuth-specific mail adapter yet;
- CRM identity resolution is email-based;
- no automatic Salesforce Lead conversion or HubSpot deal creation;
- adapters are not yet wired to autonomous workflow execution.

Those concerns are deliberately assigned to later phases rather than hidden behind a "production-ready" label.

## Next phase

**Phase 3 — Multi-Model AI & Agent Layer**

Planned scope:

- OpenAI / Claude / Gemini provider abstraction;
- structured qualification agent;
- evidence/research agent;
- bounded outreach-drafting agent;
- supervisor/orchestrator state;
- model routing and fallback contract;
- prompt versioning;
- structured-output validation;
- deterministic policy remains the final authorization layer.
