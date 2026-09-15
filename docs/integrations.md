# Integration Architecture — Phase 2

## Purpose

Phase 2 introduces bounded adapters for the external systems that a revenue-operations workflow typically touches. Business policy does not call vendor SDKs directly. Every provider sits behind a small typed contract and a normalized failure boundary.

## Supported adapters

| Capability | Adapter | External surface |
| --- | --- | --- |
| CRM | `HubSpotCRMAdapter` | HubSpot CRM v3 contacts |
| CRM | `SalesforceCRMAdapter` | Salesforce REST `Lead` sObject |
| Internal notification | `SlackWebhookNotifier` | Slack incoming webhook |
| Email | `SMTPEmailAdapter` | authenticated SMTP / STARTTLS |
| Workflow/SaaS handoff | `OutboundWebhookAdapter` | generic HTTPS webhook |

## Design rule

```text
Business workflow
      │
      ▼
provider-neutral contract
      │
      ▼
explicit field mapping
      │
      ▼
bounded HTTP / SMTP adapter
      │
      ▼
external provider
      │
      ▼
normalized result or IntegrationError
```

No provider response is trusted as business authorization. Adapters perform transport and mapping only. Policy remains in the deterministic policy layer.

## HubSpot

The adapter uses HubSpot CRM v3 contact operations:

- `POST /crm/v3/objects/contacts/search` — find a contact by email;
- `POST /crm/v3/objects/contacts` — create when no matching contact exists;
- `PATCH /crm/v3/objects/contacts/{contactId}` — update an existing contact or owner.

Authentication uses `Authorization: Bearer <token>`. The implementation writes only stable default properties plus custom properties explicitly listed in `ARO_HUBSPOT_CUSTOM_PROPERTIES`.

Reference: https://developers.hubspot.com/blog/a-developers-guide-to-hubspot-crm-objects-contacts-object

## Salesforce

The adapter maps the business entity to Salesforce's standard `Lead` sObject. This is intentional: Salesforce Lead has first-class `Company` and `LeadSource` fields, while a Contact normally belongs to an Account.

The adapter uses:

- `/services/data/latest/query` — SOQL lookup by email;
- `/services/data/latest/sobjects/Lead/` — create;
- `/services/data/latest/sobjects/Lead/{id}` — update and owner assignment.

Salesforce documents the `latest` alias for automatically resolving the current REST version. Organizations with strict change-control may pin `ARO_SALESFORCE_API_ROOT` to a specific version instead.

References:
- https://developer.salesforce.com/docs/platform/api-rest/guide/dome-versions.html
- https://developer.salesforce.com/docs/platform/api-rest/guide/resources-sobject-basic-info-post.html

## Slack

Slack notifications use incoming webhooks and send a JSON payload to the workspace/channel-specific webhook URL. The URL is itself a secret. The adapter rejects non-HTTPS endpoints and, by default, only accepts Slack webhook hosts.

Reference: https://api.slack.com/messaging/webhooks

## SMTP email

`SMTPEmailAdapter` provides a provider-neutral transactional-email boundary with optional STARTTLS and authentication. It deliberately does not assume Gmail-specific credentials or OAuth. A Gmail/Workspace API adapter can later implement the same message contract without changing workflow code.

## Generic outbound webhook

The generic webhook adapter accepts an HTTPS URL plus an event type and payload. It is suitable for n8n, Make, Zapier, internal SaaS endpoints, or other downstream workflow services.

Phase 2 does not yet sign outbound webhooks. Signing, inbound signature verification, replay defense, and allow-list policy are Phase 5 security controls.

## Error normalization

All HTTP adapters use `BoundedHttpClient` and convert provider-specific failures into `IntegrationError`:

| Condition | Kind | Retryable now? |
| --- | --- | --- |
| HTTP 400 / 422 | `validation` | no |
| HTTP 401 | `authentication` | no |
| HTTP 403 | `authorization` | no |
| HTTP 404 | `not_found` | no |
| HTTP 409 | `conflict` | no |
| HTTP 429 | `rate_limit` | yes |
| HTTP 5xx | `provider` | yes |
| timeout | `timeout` | yes |
| network failure | `network` | yes |

The `retryable` flag is evidence for the future retry policy; Phase 2 does **not** automatically retry. Bounded backoff, retry budgets, circuit breakers and DLQ behavior belong to Phase 5.

## Credentials

Credentials are loaded through `Settings` and represented as `SecretStr` where appropriate. Never place access tokens, webhook URLs, SMTP passwords or OAuth secrets in committed workflow exports or documentation.

See `.env.example` for the complete configuration surface.

## Live sandbox validation

Contract tests use `httpx.MockTransport` so CI verifies exact request/response behavior without secrets. For explicit live sandbox validation:

```bash
python scripts/integration_smoke.py hubspot
python scripts/integration_smoke.py hubspot --execute
```

The first command is always side-effect free. `--execute` must only be used after pointing environment variables at a dedicated test/sandbox destination.
