# Reproducibility

Autonomous Revenue Ops implements **Production AI Evidence Contract v1** so the repository can emit a machine-readable evidence bundle tied to the exact source revision, workflow/policy implementation, evaluation inputs, deployment contract, runtime environment, logs and checksums.

## One-command reproduction

```bash
git clone https://github.com/h00w/autonomous-revenue-ops.git
cd autonomous-revenue-ops
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
make reproduce
```

`make reproduce` runs the existing deterministic `make verify` chain and then wraps the result in Production AI Evidence Contract v1.

The default path is designed to be network-independent with respect to AI providers and SaaS side effects. Existing OpenAI, Anthropic, Gemini, HubSpot, Salesforce, Slack and SMTP smoke harnesses run in their zero-call/dry contract modes unless the operator explicitly runs live validation separately.

## Evidence output

```text
artifacts/reproduction/<UTC timestamp>-<git sha>/
├── evidence.json
├── summary.md
├── checksums.sha256
└── logs/
```

The evidence object records:

- repository commit and branch;
- tracked working-tree state;
- runtime/tool versions;
- SHA-256 identities for declared implementation, evaluation, fixture and deployment inputs;
- the complete offline verification command and result;
- generated logs and artifact hashes;
- reproduction status.

Statuses:

- `REPRODUCED` — declared verification passed from a clean tracked checkout;
- `PARTIAL` — verification passed but tracked local changes were present;
- `FAILED` — a declared input or verification step failed.

These statuses do not promote the application to **Production Validated**. Real provider/SaaS executions, long-window SLO evidence and shared transactional persistence remain separate maturity requirements.

## Why the contract matters here

Business automation can appear successful while hiding duplicate side effects, stale state, retry errors, authorization mistakes or unverifiable external actions. Reproducibility therefore binds evidence to the workflow implementation and policy revision rather than treating a successful UI run as proof.

The contract complements the repository's existing release-evidence and retained-live-validation machinery. It does not replace them.

## Checksum verification

```bash
cd artifacts/reproduction/$(cat artifacts/reproduction/LATEST)
sha256sum --check checksums.sha256
```

## Custom output location

```bash
REPRO_OUT=/tmp/aro-evidence make reproduce
```

## Clean-room standard

For publication-quality evidence:

1. checkout an immutable tag or full commit SHA;
2. start with a clean tracked working tree;
3. install dependencies from that revision;
4. run `make reproduce` without enabling live side effects;
5. retain the complete evidence bundle;
6. separately attach any live-validation evidence with exact source/release identity.

## Contract source

The canonical schema is maintained by the AI Model Release Control Center and vendored locally at:

`evidence/production-ai-evidence-contract-v1.schema.json`

The schema hash is recorded in every run.

## Updating the plan

Update `evidence/reproduction-plan.json` whenever a critical policy path, evaluation gate, deployment contract or durable-state mechanism changes. Do not weaken the plan merely to recover a green status; a failed reproduction is evidence that should remain visible until the underlying cause is resolved.
