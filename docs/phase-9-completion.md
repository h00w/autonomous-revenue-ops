# Phase 9 completion — Release Integrity & Public Proof

Phase 9 establishes an inspectable release-integrity and public-review layer around the Phase 8 deployment candidate. It strengthens reproducibility and release authorization while keeping assurance language below what has actually been proved.

## Verified pull-request evidence

The tightened Phase 9 pull-request CI run `34976221961` completed successfully on source head `eada10955b79c0a58d3000846a47788463babd79`.

| Gate | Evidence | Result |
| --- | --- | --- |
| Full Python regression suite | `python -m pytest -q` | **100/100 passed** |
| Deterministic policy benchmark | `evals/benchmark.py` | **6/6 (100%)** |
| Deterministic supervisor release gate | `evals/agent_release_gate.py` | **all required rates 100%; 0 policy violations** |
| Live-model harness default behavior | OpenAI / Anthropic / Gemini | **0 external calls** |
| Prior SaaS/workflow/reliability/analytics gates | Phase 2–8 smoke checks | **all passed** |
| Deployment hardening contract | `scripts/deployment_contract.py` | **PASS / 0 errors / 0 network calls** |
| SLO harness default behavior | `scripts/slo_probe.py` | **candidate_slo_target / 0 external calls** |
| Release version alignment | `scripts/release_version_check.py` | **PASS / expected tag v0.9.0 / 0 network calls** |
| Release evidence generation | `scripts/release_evidence.py` | **PASS** |
| Release evidence verification | `scripts/verify_release_evidence.py` | **PASS / 0 errors / 0 network calls** |
| Release-integrity artifact | GitHub Actions artifact | **ID 10399078254** |
| Release-integrity artifact ZIP digest | GitHub Actions | **sha256:8b9941a0d64641a89423ef6a581c4b629d2391fcd33cc878f58aebbfcb82ae89** |
| Agent-eval artifact | GitHub Actions artifact | **ID 10399387693** |
| Pinned runtime container build | digest-pinned Python base + exact runtime lock | **built successfully** |
| Hardened container liveness | `/health/live` | **HTTP 200 / ok** |
| Hardened container readiness | `/health/ready` | **HTTP 200 / ok** |

## Release inputs now controlled

Phase 9 adds:

- Python runtime base image pinned by SHA-256 digest;
- exact direct runtime dependency versions;
- exact transitive `requirements-api.lock` used by the production Docker build;
- source/evaluation/deployment/release-pipeline input hashing;
- release-evidence generator/verifier/version-guard scripts included in the integrity manifest;
- SPDX 2.3 runtime SBOM;
- `manifest.json` tying evidence to the exact source commit and behavior-relevant release inputs;
- `provenance.json` with source/build metadata and optional published image digest;
- `SHA256SUMS` for generated release evidence;
- verifier that recomputes both generated-evidence and tracked-source hashes;
- release version alignment across runtime and deployment manifests;
- Dependabot configuration for Python, Docker, and GitHub Actions inputs;
- `SECURITY.md`, `RELEASING.md`, release-integrity documentation and public reviewer proof path.

## Tag publication authorization

The source-controlled tag workflow requires both:

1. the tag to exactly equal `v<service_version>`; and
2. the tagged commit to be an ancestor of `origin/main`.

For service version `0.9.0`, only tag `v0.9.0` is accepted by the version contract.

The version-alignment contract is exercised in pull-request CI. The **main-ancestry check is part of the tag-triggered release workflow and has not been executed as a tag release in Phase 9 pull-request CI**. This distinction is intentional: a PR run must not be presented as evidence that a release tag was actually published.

## Supply-chain evidence boundary

Phase 9 provenance is explicitly project-generated metadata:

```text
signed = false
slsa_statement = false
```

Therefore Phase 9 does **not** claim:

- Sigstore/Cosign signing;
- keyless identity verification;
- SLSA attestation/compliance;
- independent bit-for-bit reproducible builds;
- production vulnerability-management evidence;
- that the tag-triggered GHCR/GitHub Release publication workflow has already been executed successfully.

The release workflow is source-controlled and contract-inspectable. Actual GHCR publication and GitHub Release evidence become additional retained evidence only after a valid tag on `main` triggers that workflow successfully.

## Public proof path

`docs/public-proof.md` gives a reviewer a roughly 90-second path through:

1. business problem;
2. architecture and deterministic authorization;
3. software/agent/recovery evidence;
4. hardened deployment evidence;
5. release-integrity/SBOM/provenance evidence;
6. explicit non-claims.

## Release decision

**Phase 9 pull-request release-integrity gates: PASS.**

The repository may now be described as a **release-candidate, deployment-candidate, contract-tested, security-hardened single-replica AI automation architecture with deterministic release gates, measured-runtime analytics, pinned runtime inputs, SPDX SBOM, and independently verifiable release-integrity metadata**.

It must not yet be described as **Production Validated**.

## Next milestone

Phase 10 — live validation evidence harness and retained external evidence. Live SaaS, model-provider, and deployment results must be tied to exact source commit, service version, prompt manifest, evaluation dataset, runtime release manifest and execution configuration. Harness implementation can be contract-tested without secrets; actual Production Validated claims require successful retained live evidence.
