# Phase 10 completion — Retained Live Validation Evidence

Phase 10 adds the evidence machinery required to distinguish a live-capable adapter from an actually executed, retained, source-bound validation result. It does not manufacture external validation: the provider/SaaS/deployment execution layer remains opt-in and requires real sandbox/test/staging credentials or a selected deployment.

## Verified implementation evidence

The Phase 10 implementation CI run `34980512778` completed successfully on source head `eddce60875ce9c874a4103bfbf253470ec7254e3`.

| Gate | Evidence | Result |
| --- | --- | --- |
| Full Python regression suite | `python -m pytest -q` | **116/116 passed** |
| Deterministic policy benchmark | `evals/benchmark.py` | **6/6 (100%)** |
| Deterministic supervisor release gate | `evals/agent_release_gate.py` | **all required rates 100%; 0 policy violations** |
| Live-model harness defaults | OpenAI / Anthropic / Gemini | **0 external calls** |
| SaaS integration harness defaults | HubSpot / Salesforce / Slack / SMTP | **0 external calls** |
| Deployment SLO harness default | `scripts/slo_probe.py` | **candidate_slo_target / 0 external calls** |
| Retained-evidence contract | `scripts/live_evidence_contract.py` | **PASS / 0 errors / 0 network calls** |
| Retained-evidence verifier | `scripts/verify_live_evidence.py` | **PASS / 0 errors / 0 network calls** |
| Live-validation contract artifact | GitHub Actions artifact | **ID 10400867863** |
| Live-validation contract artifact ZIP digest | GitHub Actions | **sha256:e3c5aa9d7f015059f49b6ac85b158c343de57df24d062a4f6269909d70db30c2** |
| Release version alignment | `scripts/release_version_check.py` | **PASS / expected tag v0.10.0** |
| Phase 9 release integrity | generator + verifier | **PASS / 0 errors** |
| Release-integrity artifact | GitHub Actions artifact | **ID 10400892801** |
| Release-integrity artifact ZIP digest | GitHub Actions | **sha256:c182aec3f03a5b1f228af070b48395c72dcac62bbf905f31166e078972df517d** |
| Agent-eval artifact | GitHub Actions artifact | **ID 10400753479** |
| Hardened container liveness | `/health/live` | **HTTP 200 / ok** |
| Hardened container readiness | `/health/ready` | **HTTP 200 / ok** |

The generated zero-network contract bundle itself reported SHA-256 `400d6413129eae44070e2dc0b7d46ed7b65ea3a1fa67955242a486e29b899921` for its retained `evidence.json`.

## Evidence contract introduced

Every successfully retained executed live result binds to:

- exact 40-character source commit;
- service version;
- named provider, integration, or deployment target;
- sanitized non-secret runtime fingerprint;
- prompt-manifest SHA-256 when applicable;
- evaluation-dataset SHA-256 when applicable;
- matching Phase 9 release-integrity manifest and its SHA-256;
- execution start/end timestamps;
- observed external-call count;
- typed result metrics/outcome;
- SHA-256 checksum for the retained evidence file.

Executed live evidence is rejected when the matching release manifest is missing or when its source commit/service version differs from the running source. This validation now occurs **before the external call**, so a provenance mismatch blocks the side effect rather than discovering the mismatch after execution.

Dry-run/contract evidence must record zero external calls.

## Secret and privacy boundary

Evidence generation rejects secret-bearing keys such as API keys, access tokens, passwords, authorization data and webhook URLs.

Runtime evidence retains only non-secret facts such as provider/model name, sanitized target origin, environment, service version, timeout/probe configuration and whether a credential was configured.

CRM record identifiers are retained only as SHA-256 fingerprints. Raw provider request IDs are fingerprinted where retained. Raw exception messages are not stored in live evidence; failed calls retain the exception class only.

## Retained live evidence classes

- `live_provider_smoke` — one explicitly executed provider/schema capability check;
- `live_provider_eval` — controlled agent evaluation against a named provider/model, with dataset and prompt fingerprints;
- `live_integration_smoke` — one explicitly executed sandbox/test HubSpot, Salesforce, Slack or SMTP operation;
- `live_deployment_probe` — an explicitly selected deployment liveness/readiness observation window;
- `validation_harness_contract` — zero-network CI proof that the retention machinery works; **not live validation**.

## Manual live-validation workflow

`.github/workflows/live-validation.yml` is intentionally `workflow_dispatch` only. Normal pushes and pull requests cannot trigger external provider/SaaS/deployment validation.

The manual workflow requires:

1. execution from `main`;
2. explicit acknowledgement that credentials/targets are approved sandbox, test or staging resources;
3. operation-specific credential preflight;
4. generation and verification of the exact Phase 9 release manifest before any external call;
5. retained evidence verification after execution;
6. GitHub Actions artifact upload with 90-day retention.

Deployment probes additionally require an `https://` target and are capped at 1,000 observation iterations per manual run.

The workflow supports model capability/evaluation checks for OpenAI, Anthropic and Gemini; HubSpot, Salesforce, Slack and SMTP integration smoke checks; and deployment probes.

## Release-integrity connection

Phase 9 release evidence now fingerprints the full `.github/workflows/` directory as well as the Phase 10 evaluator, integration, SLO and evidence-verification code. Changing the machinery that generates or executes live evidence therefore changes the release integrity manifest.

## What has not been executed

Phase 10 CI deliberately did **not** call:

- OpenAI;
- Anthropic;
- Gemini;
- HubSpot;
- Salesforce;
- Slack;
- SMTP;
- a public/staging deployment.

No repository secrets were read by the normal PR CI path. Therefore this phase does **not** claim that any of those external capabilities are live-validated yet.

## Maturity decision

**Phase 10 retained-evidence framework gates: PASS.**

The repository may now be described as a **release-integrity-controlled, deployment-candidate, contract-tested, security-hardened single-replica AI automation architecture with a source-bound retained live-validation framework**.

It must not yet be described as **Production Validated**.

Production/live capability claims become valid only for the specific provider/integration/deployment evidence bundles actually produced by an explicit successful manual execution. A short deployment probe is not long-window SLO attainment, and no runtime scenario/projection is customer ROI.

## Next milestone

Phase 11 should consume real retained Phase 10 artifacts rather than add another simulated layer: execute selected sandbox model/SaaS validations, validate a selected staging deployment, aggregate the retained evidence into a capability matrix, and only upgrade individual maturity labels where the corresponding exact-commit evidence exists. Horizontal replica claims remain blocked until SQLite state is migrated to a shared transactional backend and concurrency/failover behavior is validated.
