# Release integrity and supply-chain evidence

Phase 9 adds release evidence that a reviewer can independently inspect without treating metadata as stronger assurance than it provides.

## Runtime input control

The production image uses:

- a Python base image pinned by SHA-256 digest;
- exact direct runtime dependency versions;
- an exact transitive runtime lock used by the Docker build;
- `.dockerignore` and `.gitignore` boundaries preventing local secrets/state from entering the build/repository.

The exact lock is Linux/Python-3.12 oriented because it represents the validated production image environment, not a universal cross-platform lock.

## Integrity manifest

`scripts/release_evidence.py` hashes security- and behavior-relevant release inputs, including runtime source, prompts/release thresholds, agent evaluation cases, deployment manifests, dependency lock and release workflows. The manifest therefore ties a release to the exact software/governance material used to create it.

## SPDX SBOM

The release generator emits SPDX 2.3 JSON for the runtime dependency lock. Unknown license fields are reported as `NOASSERTION` rather than guessed. The SBOM is a dependency inventory; it is not a vulnerability scan or license-compliance certification.

## Provenance metadata

The generated provenance metadata records source commit, service version, builder context, base-image digest, runtime-lock hash and optional published container digest. It explicitly contains:

```text
signed = false
slsa_statement = false
```

This prevents unsigned project metadata from being presented as a signed supply-chain attestation.

## Verification

`verify_release_evidence.py` verifies generated evidence checksums, then recomputes every source checksum in the integrity manifest. Any change to a tracked source/evaluation/deployment file after evidence generation causes verification to fail.

## Tag workflow

The tag workflow reruns the software/evaluation/deployment gates before publishing. A GitHub Release is therefore downstream of the same engineering gates used for pull requests, plus release evidence generation and verification.

## Remaining boundary

Phase 9 does not yet provide keyless signing, Sigstore/Cosign verification, SLSA attestation, binary reproducibility across independent builders, or production vulnerability-management evidence. These require separate implementation and should be labeled explicitly if added later.
