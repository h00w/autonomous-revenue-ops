# Retained Live Validation Evidence

Phase 10 separates **having a live-capable adapter** from **retaining verifiable evidence that it was actually exercised**.

A successful unit test, deterministic fixture, dry-run harness, or adapter implementation is not live-provider evidence. A live claim is permitted only when an explicit execution produces a retained evidence bundle tied to the exact release inputs.

## Evidence contract

Every executed live bundle records:

- evidence class and validation ID;
- exact 40-character source commit;
- service version;
- named provider, integration, or deployment target;
- sanitized runtime fingerprint;
- prompt-manifest SHA-256 when applicable;
- evaluation-dataset SHA-256 when applicable;
- Phase 9 release-manifest SHA-256;
- start/end timestamps;
- observed external-call count;
- result metrics/outcome;
- SHA-256 checksum for the retained `evidence.json`.

Executed live evidence is rejected when the release manifest is missing, when the manifest commit/version does not match the running source, or when the recorded external-call count is zero.

Dry-run evidence must declare zero external calls.

## Secret and privacy boundary

The retained bundle never stores API keys, access tokens, passwords, authorization headers, webhook URLs, or other secret-bearing fields.

Runtime configuration records only non-secret facts such as:

- provider/model name;
- sanitized provider/deployment origin;
- environment and service version;
- whether a credential was configured;
- relevant timeout/probe parameters.

CRM record identifiers are hashed before retention. Slack webhook URLs and SMTP destination addresses are not retained.

## Evidence classes

### `live_provider_smoke`

One explicitly executed model-provider capability check. It proves that the configured provider/model returned a schema-valid response for the smoke contract at that point in time.

It does not prove task quality or production reliability.

### `live_provider_eval`

An explicitly executed evaluation of the controlled agent dataset against a named provider/model configuration. The report retains decision results and agent routing traces plus dataset/prompt fingerprints.

It is separate from `deterministic_contract_eval` and must never be inferred from the deterministic CI gate.

### `live_integration_smoke`

One explicitly executed sandbox/test integration operation for HubSpot, Salesforce, Slack, or SMTP.

The CRM record ID is retained only as SHA-256. The evidence proves the named operation succeeded for the configured sandbox/test account at that point in time; it does not prove production account permissions or long-term availability.

### `live_deployment_probe`

An explicitly executed liveness/readiness observation window against a selected deployment. Each requested observation makes one liveness and one readiness call.

A short probe is not a long-window SLO claim. Phase 10 retains the sample window and target evaluation without relabeling it as production availability history.

### `validation_harness_contract`

A zero-network CI artifact proving that the retention/verification machinery itself is operational. It is not live evidence.

## Required sequence for a real run

First generate Phase 9 release evidence from the exact commit to be validated:

```bash
export ARO_SOURCE_COMMIT="$(git rev-parse HEAD)"
python scripts/release_evidence.py --output release-evidence
python scripts/verify_release_evidence.py release-evidence
```

Then run one explicitly selected live check using sandbox/test credentials.

Model capability example:

```bash
python scripts/ai_provider_smoke.py openai \
  --execute \
  --evidence-dir live-validation-evidence/openai-smoke
python scripts/verify_live_evidence.py live-validation-evidence/openai-smoke
```

Full controlled model evaluation:

```bash
python evals/live_agent_eval.py openai \
  --execute \
  --evidence-dir live-validation-evidence/openai-eval \
  --enforce
python scripts/verify_live_evidence.py live-validation-evidence/openai-eval
```

HubSpot sandbox example:

```bash
python scripts/integration_smoke.py hubspot \
  --execute \
  --evidence-dir live-validation-evidence/hubspot-smoke
python scripts/verify_live_evidence.py live-validation-evidence/hubspot-smoke
```

Deployment observation example:

```bash
python scripts/slo_probe.py \
  --base-url https://staging.example.com \
  --target-label staging \
  --requests 100 \
  --execute \
  --evidence-dir live-validation-evidence/staging-probe \
  --enforce
python scripts/verify_live_evidence.py live-validation-evidence/staging-probe
```

## What Phase 10 does not claim

The evidence framework does **not** by itself establish:

- production validation;
- production customer authorization;
- long-window SLO attainment;
- provider/model quality beyond the retained dataset and run;
- customer ROI;
- horizontal-replica safety;
- cryptographic signing or SLSA attestation.

Those claims require the corresponding retained real-world evidence and remain explicitly separate.
