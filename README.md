# Autonomous Revenue Ops

> Production-grade AI agents, SaaS integrations, governed workflow automation, release integrity, retained validation evidence, and hardened deployment controls for revenue operations.

[![CI](https://github.com/h00w/autonomous-revenue-ops/actions/workflows/ci.yml/badge.svg)](https://github.com/h00w/autonomous-revenue-ops/actions/workflows/ci.yml)
[![Hugging Face Space](https://img.shields.io/badge/Hugging%20Face-Space-FFD21E?logo=huggingface&logoColor=000)](https://huggingface.co/spaces/h0000w/autonomous-revenue-ops)
[![Dataset](https://img.shields.io/badge/Hugging%20Face-Dataset-FFD21E?logo=huggingface&logoColor=000)](https://huggingface.co/datasets/h0000w/autonomous-revenue-ops)
[![System Card](https://img.shields.io/badge/Hugging%20Face-System%20Card-FFD21E?logo=huggingface&logoColor=000)](https://huggingface.co/h0000w/autonomous-revenue-ops)

**Proof chain:** source → typed API → structured multi-model reasoning → deterministic policy → durable workflow state → authenticated ingress → bounded/recoverable SaaS execution → deterministic release gates → operational analytics → hardened deployment → pinned release inputs + SBOM → source-bound retained live-validation framework → CI/public proof.

## Why this repository exists

Most AI automation demos prove that a happy path can run once. This repository is designed to prove harder engineering properties: typed contracts, deterministic authorization, explicit workflow state, restart recovery, idempotency, human checkpoints, bounded side effects, failure recovery, prompt/evaluation change control, operational evidence, deployment hardening, release integrity, and a disciplined separation between simulated/deterministic evidence and real external validation.

**Core rule:** AI may propose. Software validates. Policy authorizes. Durable workflow state gates execution. Bounded adapters execute. Explicit evidence determines completion and maturity.

## Project status

| Phase | Status | Verified evidence |
| --- | --- | --- |
| 0 — Foundation & publication | ✅ Complete | policy/eval skeleton, Gradio proof, HF publication path |
| 1 — Core production architecture | ✅ Complete | FastAPI, typed services/events, correlation, idempotency, health model |
| 2 — SaaS & CRM integrations | ✅ Contract-complete · 🔬 live validation pending | HubSpot, Salesforce, Slack, SMTP, webhook adapters; 41 tests at merge |
| 3 — Multi-model AI & agents | ✅ Contract-complete · 🔬 live validation pending | OpenAI/Anthropic/Gemini adapters; Research/Qualification/Outreach agents; 55 tests at merge |
| 4 — Workflow orchestration | ✅ Complete | explicit state machine, approval/research checkpoints, n8n contract; 65 tests at merge |
| 5 — Reliability, recovery & security | ✅ Complete | restart-safe SQLite, revisions, leases, retry/circuit/DLQ, API auth, signed replay-resistant webhooks; 78 tests at merge |
| 6 — Agent evaluation & release gates | ✅ Deterministic gate complete · 🔬 live model eval pending | 7-case supervisor eval, required rates 100%, 0 policy violations, prompt manifest; 82 tests at merge |
| 7 — Operational analytics & business impact | ✅ Complete | persisted-run telemetry, Prometheus metrics, measured-runtime vs scenario-projection separation; 86 tests at merge |
| 8 — Deployment hardening & SLO evidence | ✅ Complete | non-root/read-only container, K8s contract, fail-closed readiness, explicit SQLite scaling boundary; 94 tests at merge |
| 9 — Release integrity & public proof | ✅ Complete | digest-pinned base, exact runtime lock, SPDX SBOM, integrity manifest, provenance metadata, release authorization; 100 tests at merge |
| 10 — Retained live validation evidence | ✅ Framework complete · 🔬 external execution pending | source/release-bound evidence schema, verifier, manual-only live workflow, secret-safe retention; **116 tests on implementation-complete head** |

The repository is currently a **release-integrity-controlled, deployment-candidate, contract-tested, security-hardened single-replica architecture proof with a retained live-validation framework**. It is **not yet Production Validated** because the real provider/SaaS/staging executions have not been performed and retained as Phase 10 live evidence.

## End-to-end system flow

```text
Inbound lead / signed SaaS webhook / n8n
  → API authentication + HMAC/replay controls
  → typed validation + normalization
  → correlation + DB-backed idempotency
  → durable workflow run
  → Research Agent
  → Qualification Agent
  → structured-output validation
  → deterministic policy
      ├─ AUTO_ROUTE / NURTURE → READY_FOR_EXECUTION
      ├─ HUMAN_REVIEW → WAITING_HUMAN_REVIEW
      ├─ RESEARCH_MORE → WAITING_RESEARCH
      └─ BLOCK → COMPLETED without external execution
  → Outreach Agent only when policy authorizes
  → execution claim / lease
  → bounded SaaS adapters
      ├─ HubSpot
      ├─ Salesforce
      ├─ Slack
      ├─ SMTP
      └─ HTTPS webhook
  → retry / circuit breaker / persistent DLQ
  → execution receipt
  → COMPLETED / FAILED
  → persisted operational analytics
```

Release and validation path:

```text
code / prompt / schema / policy / workflow change
  → 116-test regression suite
  → 6/6 policy benchmark
  → 7-case deterministic supervisor gate
  → zero-call live/SaaS/deployment harness checks
  → deployment hardening contract
  → v0.10.0 release-version contract
  → release manifest + SPDX SBOM + provenance + SHA-256 verification
  → retained-live-evidence contract + verifier
  → hardened container build + boot
  → merge only when exact head is green

explicit manual validation only
  → main branch + sandbox/test/staging acknowledgement
  → exact release manifest verified before external call
  → selected model / SaaS / deployment check
  → secret-safe evidence bundle
  → checksum verification
  → retained GitHub Actions artifact
```

## Current verified deterministic evidence

The Phase 10 implementation-complete CI gate verifies:

| Evidence | Result |
| --- | ---: |
| Python regression suite | **116/116 passed** |
| Policy benchmark | **6/6 (100%)** |
| Structured-output success | **100%** |
| Deterministic decision accuracy | **100%** |
| Outreach/authorization agreement | **100%** |
| Routing/trace integrity | **100%** |
| Prompt boundary integrity | **100%** |
| Policy violations | **0** |
| Agent evaluation cases | **7** |
| OpenAI/Anthropic/Gemini default external calls | **0** |
| HubSpot/Salesforce/Slack/SMTP default external calls | **0** |
| SLO dry-run external calls | **0** |
| Retained-evidence contract | **PASS / 0 network calls** |
| Release version contract | **PASS / v0.10.0** |
| Release-integrity verification | **PASS / 0 errors** |
| Hardened container liveness | **HTTP 200 / ok** |
| Hardened container readiness | **HTTP 200 / ok** |
| Container runtime identity | **UID/GID 10001:10001** |

The 100% agent metrics are **deterministic contract/governance evidence using controlled fixtures**. They are not presented as OpenAI, Anthropic, or Gemini accuracy. Normal PR CI reads no live-provider/SaaS secrets and performs no live external validation.

## Production controls

| Control area | Implementation |
| --- | --- |
| Domain/API contracts | `src/models.py`, FastAPI/Pydantic |
| Deterministic authorization | `src/policy.py` |
| Multi-model structured generation | `src/ai/` |
| Prompt change control | `src/ai/prompts.py`, `evals/prompt_manifest.json` |
| Agent supervision | `src/ai/supervisor.py` |
| Durable workflow state | `src/orchestration/` |
| Idempotency / stale-writer protection | `src/orchestration/store.py` |
| Human/research checkpoints | `src/orchestration/engine.py` |
| Retry / circuit breaker / DLQ | `src/reliability.py` |
| API authentication | `src/security/auth.py` |
| Signed/replay-protected webhooks | `src/security/webhooks.py` |
| HubSpot / Salesforce / Slack / SMTP | `src/integrations/` |
| Operational analytics | `src/analytics/` |
| Measured-vs-scenario boundary | `src/analytics/impact.py` |
| Deployment readiness | `src/operations/readiness.py` |
| Candidate/live SLO model | `src/operations/slo.py`, `scripts/slo_probe.py` |
| Hardened API image | `Dockerfile`, `docker-compose.yml` |
| Kubernetes reference | `deploy/k8s/` |
| Release integrity / SBOM | `scripts/release_evidence.py`, `scripts/verify_release_evidence.py` |
| Release authorization | `scripts/release_version_check.py`, `.github/workflows/release.yml` |
| Retained live evidence | `src/evidence/`, `scripts/verify_live_evidence.py` |
| Manual external validation | `.github/workflows/live-validation.yml` |
| Regression/eval evidence | `tests/`, `evals/`, `.github/workflows/ci.yml` |

## Deployment boundary

The durable workflow/security stores are still SQLite. The reference production topology therefore deliberately remains **single replica**:

- Kubernetes `replicas: 1`;
- `Recreate` deployment strategy;
- `ReadWriteOnce` persistent volume;
- runtime `ARO_DEPLOYMENT_REPLICA_COUNT=1`;
- production readiness fails if SQLite is paired with more than one application replica.

This is a safety constraint, not a scalability claim. Horizontal application replicas require a shared transactional persistence layer plus concurrency/failover validation.

The reference runtime also enforces non-root execution, read-only root filesystem, dropped Linux capabilities, no privilege escalation, RuntimeDefault seccomp, bounded resources, liveness/readiness probes, and external secret references.

## Evidence classes

Evidence labels are explicit so demos cannot silently become production claims:

- `deterministic_contract_eval` — CI agent/policy/software invariants;
- `measured_runtime` — aggregates calculated from persisted workflow records;
- `scenario_projection` — hypothetical time/cost/business impact, **not measured customer ROI**;
- `static_deployment_contract` — manifest/container policy validation without a deployment call;
- `container_runtime_smoke` — hardened local container boot/health proof;
- `candidate_slo_target` — configured engineering target only;
- `validation_harness_contract` — zero-network proof that retained-evidence machinery works;
- `live_provider_smoke` — one explicitly executed provider capability check;
- `live_provider_eval` — explicitly executed controlled model evaluation with prompt/dataset fingerprints;
- `live_integration_smoke` — explicitly executed sandbox/test SaaS operation;
- `live_deployment_probe` — explicitly executed liveness/readiness observation window.

Every retained live class remains bounded by `production_validated=false`. A single successful smoke/eval/probe upgrades only that exact capability claim, not the whole system.

## Release integrity

Phase 9/10 release evidence contains:

- digest-pinned Python base image;
- exact direct and transitive runtime dependencies;
- SPDX 2.3 runtime SBOM;
- source/evaluation/deployment/workflow SHA-256 manifest;
- project-generated provenance metadata;
- `SHA256SUMS` verification;
- release tag/version alignment.

The provenance remains intentionally honest:

```text
signed = false
slsa_statement = false
```

No Sigstore/Cosign or SLSA claim is made.

## Retained live validation

A real execution must first generate and verify release evidence from the exact commit:

```bash
export ARO_SOURCE_COMMIT="$(git rev-parse HEAD)"
python scripts/release_evidence.py --output release-evidence
python scripts/verify_release_evidence.py release-evidence
```

Then execute a selected sandbox/test check with an evidence directory:

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
  --enforce \
  --evidence-dir live-validation-evidence/openai-eval
```

SaaS example:

```bash
python scripts/integration_smoke.py hubspot \
  --execute \
  --evidence-dir live-validation-evidence/hubspot-smoke
```

Deployment example:

```bash
python scripts/slo_probe.py \
  --base-url https://staging.example.com \
  --target-label staging \
  --requests 100 \
  --execute \
  --enforce \
  --evidence-dir live-validation-evidence/staging-probe
```

For repository-managed execution, use **Actions → Retained Live Validation → Run workflow** on `main`. The workflow is manual-only, requires an explicit sandbox/test/staging acknowledgement, verifies release provenance before the external call, performs operation-specific credential preflight, verifies the resulting evidence, and uploads it as a retained artifact.

## Run locally

```bash
git clone https://github.com/h00w/autonomous-revenue-ops.git
cd autonomous-revenue-ops
python -m venv .venv
python -m pip install -r requirements.txt
cp .env.example .env
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

Build the hardened API image:

```bash
docker build -t autonomous-revenue-ops:0.10.0 .
```

Run the entire non-network verification chain:

```bash
make verify
```

## Key endpoints

- `GET /health/live` — shallow process liveness
- `GET /health/ready` — deployment readiness; 503 when production requirements are missing
- `POST /v1/leads/evaluate` — governed direct evaluation
- `POST /v1/workflows/leads` — create/replay a workflow
- `GET /v1/workflows/runs/{run_id}` — inspect durable state
- `POST /v1/workflows/runs/{run_id}/approval` — human approval/rejection
- `POST /v1/workflows/runs/{run_id}/resume-research` — resume research checkpoint
- `POST /v1/workflows/runs/{run_id}/claim` — claim authorized execution
- `POST /v1/workflows/runs/{run_id}/complete` — record execution receipt
- `POST /v1/workflows/recover` — recover persisted stalled runs
- `POST /v1/webhooks/lead` — signed/replay-protected lead ingress
- `GET /v1/analytics/summary` — persisted-run analytics
- `GET /v1/analytics/metrics` — Prometheus-compatible aggregate metrics
- `POST /v1/analytics/impact` — explicitly labeled scenario projection

## Documentation

### Architecture, integrations, agents and operations
- [System design](docs/system-design.md)
- [Integration architecture](docs/integrations.md)
- [Agent architecture](docs/agent-architecture.md)
- [Workflow orchestration](docs/workflow-orchestration.md)
- [Reliability architecture](docs/reliability-architecture.md)
- [Security controls](docs/security.md)
- [Recovery runbook](docs/recovery-runbook.md)
- [Operational analytics](docs/operational-analytics.md)
- [Deployment architecture](docs/deployment-architecture.md)
- [SLO evidence model](docs/slo-evidence.md)
- [Retained live validation evidence](docs/live-validation-evidence.md)
- [90-second public proof](docs/public-proof.md)

### Phase completion records
- [Phase 1](docs/phase-1-completion.md)
- [Phase 2](docs/phase-2-completion.md)
- [Phase 3](docs/phase-3-completion.md)
- [Phase 4](docs/phase-4-completion.md)
- [Phase 5](docs/phase-5-completion.md)
- [Phase 6](docs/phase-6-completion.md)
- [Phase 7](docs/phase-7-completion.md)
- [Phase 8](docs/phase-8-completion.md)
- [Phase 9](docs/phase-9-completion.md)
- [Phase 10](docs/phase-10-completion.md)

### Key ADRs
- [ADR-005: AI recommends; deterministic policy authorizes](docs/adr/005-ai-recommends-policy-authorizes.md)
- [ADR-007: Workflow state outside agents](docs/adr/007-orchestration-state-outside-agents.md)
- [ADR-008: SQLite restart-safe workflow store](docs/adr/008-sqlite-durable-workflow-store.md)
- [ADR-009: Authenticate webhooks before parsing](docs/adr/009-authenticate-webhooks-before-parsing.md)
- [ADR-010: Separate deterministic and live-model evidence](docs/adr/010-separate-deterministic-and-live-model-evidence.md)
- [ADR-011: Separate measured runtime from business-impact scenarios](docs/adr/011-separate-measured-and-scenario-evidence.md)
- [ADR-012: Keep SQLite deployment single-replica](docs/adr/012-single-replica-sqlite-deployment-boundary.md)
- [ADR-014: Bind live validation to exact release manifest](docs/adr/014-retain-live-evidence-against-release-manifest.md)

## Hugging Face publication

- Space: https://huggingface.co/spaces/h0000w/autonomous-revenue-ops
- Dataset: https://huggingface.co/datasets/h0000w/autonomous-revenue-ops
- System/model card: https://huggingface.co/h0000w/autonomous-revenue-ops
- Bucket: https://huggingface.co/buckets/h0000w/autonomous-revenue-ops

GitHub remains the source of truth. Hugging Face publication is a public review surface, not a substitute for repository release/evidence gates.

## Current maturity boundary

This repository has deterministic software/agent evidence, durable orchestration, reliability/security controls, measured-runtime analytics, hardened single-replica deployment proof, pinned release inputs, SBOM/integrity metadata, and a retained external-validation framework.

It is **not yet Production Validated**. Remaining evidence includes actual retained model/SaaS/staging executions, meaningful live deployment observation windows, and shared transactional persistence before any horizontal-replica claim.

Synthetic demonstration values and scenario projections are never presented as customer ROI.

## Author

**Hendarmawan, PhD Eng.**  
Production AI · Agentic Systems · AI Automation · Secure AI Infrastructure

Website: https://hendarmawan.se · GitHub: https://github.com/h00w
