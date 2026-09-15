# Security Policy

## Supported branch

Security fixes are applied to the current `main` branch. Tagged releases are immutable evidence points; a security fix is published as a new release rather than rewriting a previous release.

## Reporting a vulnerability

Do not include exploit details, credentials, personal data, tokens, or sensitive customer information in a public issue.

Prefer GitHub's private security-advisory / private vulnerability-reporting channel for this repository when available. If a private reporting channel is not available, open a public issue containing only a request for a private contact path and enough non-sensitive metadata to identify the affected component. Do not publish reproduction details until a private channel is established.

Useful report metadata includes the affected commit/tag, component, deployment mode, impact, preconditions, and whether the issue can cross an authentication, policy, workflow-state, or external-action boundary.

## Security boundaries

The repository deliberately treats the following as security-sensitive boundaries:

- API authentication and webhook HMAC/replay validation;
- untrusted lead/CRM/research content entering model prompts;
- deterministic policy authorization of external actions;
- executor leases and idempotent execution receipts;
- secret/configuration separation from source control;
- SQLite single-replica deployment constraint;
- release/source/evaluation integrity evidence.

## Secret handling

Secrets belong in environment-specific secret stores or GitHub Actions secrets. `.env`, runtime databases, generated evidence, and Kubernetes Secret values must not be committed. If a credential is accidentally committed, revoke/rotate it immediately; deleting the current file is not sufficient because Git history may retain it.

## Evidence integrity

Phase 9 generates an SPDX SBOM, source/evaluation/deployment integrity manifest, checksums, and provenance metadata. The provenance metadata explicitly records that it is **not cryptographically signed and not a SLSA attestation**. A future signed-attestation phase must not retroactively relabel unsigned evidence.
