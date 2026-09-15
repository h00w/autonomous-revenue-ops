# ADR-013: Unsigned project provenance is not a SLSA attestation

## Status
Accepted for Phase 9.

## Context
Release metadata is useful for tying source, dependency locks, evaluation inputs, deployment configuration and image digests together. However, project-generated JSON without cryptographic signing does not provide the identity/integrity guarantees of a signed supply-chain attestation.

## Decision
Phase 9 emits `build_provenance_metadata` with explicit fields `signed: false` and `slsa_statement: false`. Documentation must call it provenance metadata, not SLSA provenance/attestation. Release integrity is additionally protected with SHA-256 checksums and source-file re-verification.

## Consequences
Reviewers can reconstruct what inputs a release references and detect evidence/source drift, while assurance language remains accurate. Signed keyless attestations, Sigstore/Cosign verification and any SLSA-level claim are deferred until they are actually implemented and validated.
