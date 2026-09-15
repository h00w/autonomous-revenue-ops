# Integration Contracts

## CRM contract

All CRM providers implement the `CRMAdapter` protocol:

```python
class CRMAdapter(Protocol):
    provider: str
    def find_by_email(self, email: str) -> CRMUpsertResult | None: ...
    def upsert_lead(self, lead: CRMLeadRecord) -> CRMUpsertResult: ...
    def update_owner(self, record_id: str, owner_id: str) -> CRMUpsertResult: ...
    def close(self) -> None: ...
```

This keeps business workflow code independent from HubSpot or Salesforce object shapes.

## CRM input contract

`CRMLeadRecord` contains only provider-neutral state:

| Field | Required | Purpose |
| --- | --- | --- |
| `external_key` | yes | originating business/workflow ID |
| `email` | yes | identity lookup key used in Phase 2 |
| `first_name` | no | contact/lead first name |
| `last_name` | yes | contact/lead last name |
| `company` | yes | company name |
| `title` | no | role/job title |
| `source` | no | acquisition source |
| `owner_id` | no | provider owner identifier |
| `attributes` | no | candidate custom properties; only allow-listed keys are written |

## CRM result contract

```json
{
  "provider": "hubspot",
  "record_id": "12345",
  "created": true,
  "updated": false,
  "raw": {}
}
```

A successful adapter operation returns a provider record ID and whether the operation created or updated state. Workflow code should rely on the normalized fields; `raw` is diagnostic evidence and should not be treated as a stable cross-provider schema.

## Error contract

Adapters raise `IntegrationError`, which contains:

- `provider`
- normalized `kind`
- human-readable message
- `retryable`
- optional HTTP status
- optional `Retry-After` seconds
- provider detail payload

This prevents workflow code from branching on vendor-specific exception classes or response text.

## Notification contract

`NotificationResult` exposes:

```json
{
  "provider": "slack",
  "delivered": true,
  "provider_message_id": null,
  "status_code": 200
}
```

SMTP and Slack/webhook delivery therefore expose a comparable success signal even though the transports differ.

## Contract-testing policy

CI tests external boundaries with deterministic fakes/mocks rather than public internet calls. Tests must prove:

1. correct HTTP method and resource path;
2. correct bearer/auth behavior;
3. explicit provider field mapping;
4. create-vs-update behavior;
5. owner update scope;
6. custom-field allow-list enforcement;
7. normalization of auth, validation, conflict, rate-limit, provider and timeout failures;
8. no secret is required for repository tests.

Live-provider validation is a separate evidence class and is only performed with explicit sandbox/test credentials through `scripts/integration_smoke.py`.
