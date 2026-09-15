# ADR-014: Bind live validation evidence to the exact release manifest

## Status

Accepted for Phase 10.

## Context

The repository already separates deterministic contract evidence from opt-in live provider/deployment checks. Before Phase 10, however, a successful live command could be observed in terminal output without a durable proof object tying that result to the exact source commit, prompt manifest, evaluation dataset, runtime configuration, and Phase 9 release integrity manifest.

That is insufficient for a production-grade evidence chain because the same provider name or script path can represent materially different code/configuration over time.

## Decision

Every executed live provider, SaaS integration, or deployment probe must emit a retained validation bundle that:

1. records the exact source commit and service version;
2. requires a matching Phase 9 `release-evidence/manifest.json`;
3. fingerprints prompt/dataset materials when applicable;
4. records only secret-safe runtime metadata;
5. records an observed external-call count greater than zero;
6. stores result metrics/outcomes and an explicit evidence class;
7. includes a SHA-256 checksum for the retained evidence file;
8. keeps `production_validated=false` unless a later, separate evidence decision explicitly changes the project maturity state.

Dry-run/CI contract evidence must record zero external calls and cannot satisfy live-validation requirements.

## Consequences

A live result is harder to create casually, but materially easier to audit. Evidence from one commit/configuration cannot be silently reused for another. Missing release provenance becomes a hard failure instead of a documentation caveat.

The evidence bundles remain project-generated metadata rather than cryptographically signed attestations. Phase 9 signing/SLSA limitations still apply.
