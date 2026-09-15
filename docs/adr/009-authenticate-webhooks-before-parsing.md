# ADR-009: Authenticate raw webhooks before parsing or orchestration

## Status
Accepted.

## Decision
Verify an HMAC-SHA256 signature over the timestamp and exact raw request body before deserializing user-controlled content or invoking any workflow logic. Persist replay fingerprints for the acceptance window.

## Rationale
Parsing or acting on an unauthenticated request expands the attack surface and makes exact signature verification harder. Timestamp validation limits capture lifetime; persistent replay records prevent reuse of a still-valid signed request after process restart.

## Consequences
Webhook senders must share a secret and maintain reasonable clock synchronization. Secret rotation needs explicit operational coordination.
