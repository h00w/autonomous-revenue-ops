# Release process

Releases are evidence points, not just version labels. A tag should identify the exact source, runtime dependency lock, evaluation inputs, deployment contract and container image associated with that release.

## Preconditions

1. `main` CI is green.
2. `make verify` passes locally or in CI.
3. Phase completion/maturity language is accurate.
4. No live-provider or production-SLO claim is added without retained evidence.
5. Runtime dependencies and base image changes have been reviewed.

## Release evidence

Generate and verify locally:

```bash
python scripts/release_evidence.py --output release-evidence
python scripts/verify_release_evidence.py release-evidence
```

The bundle contains:

- `manifest.json` — source/evaluation/deployment hashes and evidence boundaries;
- `sbom.spdx.json` — SPDX 2.3 runtime dependency inventory derived from the exact runtime lock;
- `provenance.json` — source/build metadata and optional published image digest;
- `SHA256SUMS` — integrity checksums for the generated evidence files.

`provenance.json` is project-generated metadata. It is deliberately marked unsigned and is not presented as a SLSA attestation.

## Tag release

Use a semantic tag after the version is aligned in runtime configuration/manifests, for example:

```bash
git tag v0.9.0
git push origin v0.9.0
```

The tag workflow reruns the verification gates, generates release evidence, builds and pushes the image to GHCR, records the published image digest in regenerated provenance metadata, verifies the evidence bundle, uploads the bundle as a workflow artifact, and creates/updates the GitHub Release asset.

## Immutability

Do not move an already published release tag. If a release is wrong, publish a new patch tag and document the superseded release.
