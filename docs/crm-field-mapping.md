# CRM Field Mapping

The application owns a provider-neutral `CRMLeadRecord`. Adapters translate that record into provider fields. This document is authoritative for the Phase 2 mapping and intentionally avoids pretending that HubSpot Contacts and Salesforce Leads have identical schemas.

## Canonical → HubSpot Contact

| Canonical field | HubSpot property | Notes |
| --- | --- | --- |
| `email` | `email` | used as Phase 2 identity lookup |
| `first_name` | `firstname` | omitted if blank |
| `last_name` | `lastname` | required by canonical contract |
| `company` | `company` | text property on Contact |
| `title` | `jobtitle` | omitted if absent |
| `owner_id` | `hubspot_owner_id` | only written when explicitly supplied |
| `source` | — | not written by default to avoid assuming a portal-specific source property |
| `attributes[key]` | custom property `key` | only if `key` is present in `ARO_HUBSPOT_CUSTOM_PROPERTIES` |

HubSpot upsert behavior in this phase is deterministic:

```text
search Contact by email
  ├─ found     → PATCH contact/{id}
  └─ not found → POST contacts
```

## Canonical → Salesforce Lead

| Canonical field | Salesforce Lead field | Notes |
| --- | --- | --- |
| `email` | `Email` | used as Phase 2 identity lookup |
| `first_name` | `FirstName` | omitted if blank |
| `last_name` | `LastName` | standard Lead requirement |
| `company` | `Company` | standard Lead requirement |
| `title` | `Title` | optional |
| `source` | `LeadSource` | value must be valid for the target org's picklist configuration |
| `owner_id` | `OwnerId` | explicit provider user/queue ID |
| `attributes[key]` | custom field `key` | only if `key` is present in `ARO_SALESFORCE_CUSTOM_FIELDS` |

The Salesforce adapter uses the `Lead` object rather than `Contact` because the revenue-operations object at this stage is an unconverted lead and `Company` is a first-class Lead field.

## Name handling

The system does not fabricate identity data:

- `Ada Lovelace` → `first_name= Ada`, `last_name=Lovelace`
- `Mary Jane Watson` → `first_name=Mary Jane`, `last_name=Watson`
- `Madonna` → `first_name=""`, `last_name=Madonna`

## Custom-field governance

Arbitrary model/agent output must never become an arbitrary CRM property write. Custom state follows this sequence:

```text
agent/evaluation output
      ↓
candidate attributes
      ↓
explicit configuration allow-list
      ↓
provider field write
```

Examples:

```env
ARO_HUBSPOT_CUSTOM_PROPERTIES=aro_score,aro_segment
ARO_SALESFORCE_CUSTOM_FIELDS=Lead_Score__c,ARO_Segment__c
```

If a candidate attribute is not on the allow-list, the adapter drops it rather than guessing that the provider supports it.

## Identity limitation

Email is used as the Phase 2 lookup key for demonstration and integration proof. Enterprise deployments may require provider-native external IDs, account/contact resolution, merged identities, or domain-specific deduplication. Those concerns belong to later data/reliability work and must be defined before production migration.
