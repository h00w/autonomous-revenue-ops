# ADR-003: Use a Provider-Neutral CRM Contract with Explicit Mappers

- **Status:** Accepted
- **Date:** 2026-09-15

## Context

HubSpot Contacts and Salesforce Leads are different domain objects with different required fields, ownership models and custom-field conventions. Embedding provider JSON directly into workflow logic would make policy and orchestration vendor-specific.

## Decision

Introduce `CRMLeadRecord` and the `CRMAdapter` protocol as the stable business-facing contract. Each provider owns an explicit mapper:

- HubSpot → Contact properties;
- Salesforce → Lead sObject fields.

Arbitrary custom attributes are never forwarded by default. A field/property must be explicitly allow-listed in runtime configuration before the adapter writes it.

## Consequences

### Positive

- workflow and policy code does not depend on vendor JSON;
- provider swaps do not change the canonical lead schema;
- field writes are inspectable and bounded;
- custom fields can be governed per deployment.

### Trade-offs

- some provider-specific capabilities are intentionally hidden behind the common interface;
- complex account/contact conversion will require specialized services later;
- field mapping must be maintained as a versioned contract.
