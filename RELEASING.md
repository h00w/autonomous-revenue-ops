# Release process

Releases are evidence points, not just version labels. A tag identifies the exact source, runtime dependency lock, evaluation inputs, deployment contract and container image associated with that release.

## Preconditions

1. Merge the release candidate to `main` and confirm `main` CI is green.
2. `make verify` passes locally or in CI.
3. `python scripts/release_version_check.py` passes.
4. Phase completion/maturity language is accurate.
5. No live-provider or production-SLO claim is added without retained evidence.
6. Runtime dependencies and base-image changes have been reviewed.

## Version contract

A release tag must be exactly `v<service_version>`. Phase 9 validates the service version against `.env.example`, Docker Compose and Kubernetes manifests. The release workflow also fetches `main` and requires the tagged commit to be an ancestor of `origin/main`; a tag created only on an unmerged side branch is rejected before package publication.

For version `0.9.0`, the only accepted release tag is:

```bash
v0.9.0
```

## Release evidence

Generate and verify locally:

```bash
python scripts/release_evidence.py --output release-evidence
python scripts/verify_release_evidence.py release-evidence
```

The bundle contains:

- `manifest.json` — source/evaluation/deployment/release-pipeline hashes and evidence boundaries;
- `sbom.spdx.json` — SPDX 2.3 runtime dependency inventory derived from the exact runtime lock;
- `provenance.json` — source/build metadata and optional published image digest;
- `SHA256SUMS` — integrity checksums for generated evidence files.

`provenance.json` is project-generated metadata. It is deliberately marked unsigned and is not presented as a SLSA attestation.

## Tag release

After the exact release commit is present on `main`:

```bash
git checkout main
git pull --ff-only
git tag v0.9.0
git push origin v0.9.0
```

The tag workflow validates tag/version/main ancestry, reruns verification gates, generates release evidence, builds and pushes the image to GHCR, records the published image digest in regenerated provenance metadata, verifies the evidence bundle, uploads the bundle as a workflow artifact, and creates/updates the GitHub Release asset.

## Immutability

Do not move an already published release tag. If a release is wrong, publish a new patch tag and document the superseded release.
