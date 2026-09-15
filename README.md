# Autonomous Revenue Ops

> Production-grade AI agents, SaaS integrations, governed workflow automation, operational evidence, and hardened deployment controls for revenue operations.

[![CI](https://github.com/h00w/autonomous-revenue-ops/actions/workflows/ci.yml/badge.svg)](https://github.com/h00w/autonomous-revenue-ops/actions/workflows/ci.yml)
[![Hugging Face Space](https://img.shields.io/badge/Hugging%20Face-Space-FFD21E?logo=huggingface&logoColor=000)](https://huggingface.co/spaces/h0000w/autonomous-revenue-ops)
[![Dataset](https://img.shields.io/badge/Hugging%20Face-Dataset-FFD21E?logo=huggingface&logoColor=000)](https://huggingface.co/datasets/h0000w/autonomous-revenue-ops)
[![System Card](https://img.shields.io/badge/Hugging%20Face-System%20Card-FFD21E?logo=huggingface&logoColor=000)](https://huggingface.co/h0000w/autonomous-revenue-ops)

**Proof chain:** source → typed API → structured multi-model reasoning → deterministic policy → durable workflow state → authenticated ingress → bounded/recoverable execution → deterministic release gates → measured-runtime analytics → hardened container/deployment contract → CI evidence → public reviewer surfaces.

## Why this repository exists

Most AI-automation demos prove only that a happy-path workflow can run once. This repository is structured to prove the harder engineering properties: typed contracts, deterministic authorization, explicit workflow state, idempotency, restart recovery, human approval, bounded external actions, failure handling, prompt/evaluation change control, operational analytics, security boundaries, and deployable runtime behavior.

**Core rule:** AI may propose. Software validates. Policy authorizes. Durable workflow state gates execution. Bounded adapters execute. Explicit evidence determines completion.

## Project status

| Phase | Status | Verified evidence |
| --- | --- | --- |
| 0 — Foundation & publication | ✅ Complete | policy/eval skeleton, Gradio proof, HF sync |
| 1 — Core production architecture | ✅ Complete | FastAPI, typed services/events, correlation, idempotency, health model |
| 2 — SaaS & CRM integrations | ✅ Contract-complete · 🔬 live validation pending | HubSpot, Salesforce, Slack, SMTP, webhook adapters; 41 tests at merge |
| 3 — Multi-model AI & agents | ✅ Contract-complete · 🔬 live validation pending | OpenAI/Anthropic/Gemini adapters; Research/Qualification/Outreach agents; 55 tests at merge |
| 4 — Workflow orchestration | ✅ Complete | explicit state machine, approval/research checkpoints, n8n contract; 65 tests at merge |
| 5 — Reliability, recovery & security | ✅ Complete | restart-safe SQLite, revisions, leases, recovery, retry/circuit/DLQ, API auth, signed replay-resistant webhooks; 78 tests at merge |
| 6 — Agent evaluation & release gates | ✅ Deterministic gate complete · 🔬 live model eval pending | 7-case supervisor eval, all required rates 100%, 0 policy violations, prompt manifest, CI artifact; 82 tests at merge |
| 7 — Operational analytics & business impact | ✅ Complete | persisted-run telemetry, Prometheus metrics, measured-runtime vs scenario-projection separation; 86 tests at merge |
| 8 — Deployment hardening & SLO evidence | ✅ Complete | non-root/read-only container, K8s contract, fail-closed production readiness, SLO evidence classes; **94 tests**, hardened container boot verified |
| 9 — Release & public proof | ⏭ Next | release manifest, SBOM/provenance, integrity bundle, security/release docs, recruiter-facing proof |
| 10 — Live-provider production validation | Planned | retained live SaaS/model/deployment evidence tied to exact commit/config |

The maturity boundary is intentional: the repository is currently a **deployment-candidate, contract-tested, hardened single-replica architecture proof**. It is **not yet Production Validated**. Live SaaS/model capability evidence, long-window deployment SLO evidence, and a shared transactional persistence layer for horizontal replicas remain separate requirements.

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

Release path:

```text
code / prompt / schema / policy change
  → 94-test regression suite
  → 6/6 policy benchmark
  → 7-case deterministic supervisor gate
  → prompt manifest/version/hash validation
  → side-effect-free provider/SaaS smoke gates
  → analytics evidence-separation gate
  → deployment contract gate
  → hardened container build + boot
  → CI evidence artifact
  → merge only when green
```

## Current verified evidence

The Phase 8 exact-head CI gate verifies:

| Evidence | Result |
| --- | ---: |
| Python regression suite | **94/94 passed** |
| Policy benchmark | **6/6 (100%)** |
| Structured-output success | **100%** |
| Deterministic decision accuracy | **100%** |
| Outreach/authorization agreement | **100%** |
| Routing/trace integrity | **100%** |
| Prompt boundary integrity | **100%** |
| Policy violations | **0** |
| Agent evaluation cases | **7** |
| Static deployment contract | **PASS / 0 errors** |
| SLO dry-run external calls | **0** |
| Hardened container liveness | **HTTP 200 / ok** |
| Hardened container readiness | **HTTP 200 / ok** |
| Container runtime identity | **UID/GID 10001:10001** |

The 100% agent metrics above are **deterministic contract/governance evidence** using controlled fixtures. They are not presented as OpenAI, Anthropic, or Gemini model accuracy.

## Production controls

| Control area | Implementation |
| --- | --- |
| Domain/API contracts | `src/models.py`, FastAPI/Pydantic |
| Deterministic authorization | `src/policy.py` |
| Multi-model structured generation | `src/ai/` |
| Prompt version/change control | `src/ai/prompts.py`, `evals/prompt_manifest.json` |
| Agent supervision | `src/ai/supervisor.py` |
| Durable workflow state | `src/orchestration/` |
| Idempotency + stale-writer protection | `src/orchestration/store.py` |
| Human/research checkpoints | `src/orchestration/engine.py` |
| Executor leases / claims | `src/orchestration/store.py`, `src/orchestration/engine.py` |
| Retry / circuit breaker / DLQ | `src/reliability.py` |
| API authentication | `src/security/auth.py` |
| HMAC webhook + replay protection | `src/security/webhooks.py` |
| HubSpot / Salesforce / Slack / SMTP | `src/integrations/` |
| Operational analytics | `src/analytics/` |
| Measured-vs-scenario evidence boundary | `src/analytics/impact.py` |
| Prometheus-compatible aggregate metrics | `GET /v1/analytics/metrics` |
| Deployment readiness | `src/operations/readiness.py` |
| Candidate/live SLO evidence model | `src/operations/slo.py`, `scripts/slo_probe.py` |
| Deployment hardening validator | `scripts/deployment_contract.py` |
| Hardened API image | `Dockerfile`, `docker-compose.yml` |
| Kubernetes reference | `deploy/k8s/` |
| Regression/eval evidence | `tests/`, `evals/`, `.github/workflows/ci.yml` |

## Deployment boundary

The current durable store is SQLite. Phase 8 therefore deliberately validates a **single application replica**:

- Kubernetes `replicas: 1`;
- `Recreate` deployment strategy;
- `ReadWriteOnce` persistent volume;
- runtime `ARO_DEPLOYMENT_REPLICA_COUNT=1`;
- production readiness fails if SQLite is configured with more than one application replica.

This is a safety constraint, not a scalability claim. Horizontal application replicas require migration of workflow/idempotency/replay state to a shared transactional backend followed by concurrency/failover validation.

The reference container/Kubernetes runtime also enforces non-root execution, a read-only root filesystem, dropped Linux capabilities, no privilege escalation, RuntimeDefault seccomp, bounded resources, liveness/readiness probes, and external secret references.

## Evidence classes

The project keeps evidence types explicit so demos are not mislabeled as production results:

- `deterministic_contract_eval` — CI agent/policy/software invariants;
- `measured_runtime` — aggregates calculated from persisted workflow records;
- `scenario_projection` — hypothetical time/cost/business impact from explicit assumptions, **not measured customer ROI**;
- `static_deployment_contract` — manifest/container-policy validation without a deployment call;
- `container_runtime_smoke` — locally built hardened container boot/health proof;
- `candidate_slo_target` — configured SLO engineering target only;
- `live_deployment_probe` — emitted only by an explicitly executed probe against a selected deployment;
- `live_provider_eval` — retained live model evaluation, separate from deterministic CI evidence.

## Run locally

```bash
git clone https://github.com/h00w/autonomous-revenue-ops.git
cd autonomous-revenue-ops
python -m venv .venv
python -m pip install -r requirements.txt
cp .env.example .env
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

Or build the API image:

```bash
docker build -t autonomous-revenue-ops:0.8.0 .
```

`make verify` runs the local non-network verification chain, including regression tests, policy/agent gates, smoke harnesses, analytics evidence checks, deployment-contract validation and SLO dry-run validation.

## Key endpoints

- `GET /health/live` — shallow process liveness
- `GET /health/ready` — deployment readiness; returns 503 when production requirements are missing
- `POST /v1/leads/evaluate` — governed direct evaluation
- `POST /v1/workflows/leads` — create/replay a workflow
- `GET /v1/workflows/runs/{run_id}` — inspect durable state
- `POST /v1/workflows/runs/{run_id}/approval` — human approval/rejection
- `POST /v1/workflows/runs/{run_id}/resume-research` — resume research checkpoint
- `POST /v1/workflows/runs/{run_id}/claim` — claim authorized execution
- `POST /v1/workflows/runs/{run_id}/complete` — record execution receipt
- `POST /v1/workflows/recover` — recover persisted stalled runs
- `POST /v1/webhooks/lead` — signed/replay-protected lead ingress
- `GET /v1/analytics/summary` — aggregate persisted-run analytics
- `GET /v1/analytics/metrics` — Prometheus-compatible aggregate metrics
- `POST /v1/analytics/impact` — explicitly labeled scenario projection

## Verification and opt-in live evidence

Required deterministic gate:

```bash
make verify
```

Opt-in live model evaluation:

```bash
python evals/live_agent_eval.py openai
python evals/live_agent_eval.py openai --execute --report openai-live-eval.json
```

Opt-in deployment SLO probe:

```bash
python scripts/slo_probe.py
python scripts/slo_probe.py --base-url https://staging.example.com --requests 100 --execute --enforce
```

Without the explicit execution flags, these harnesses make no external model/deployment calls.

## Documentation

### Architecture and integrations
- [System design](docs/system-design.md)
- [Event / correlation / idempotency](docs/event-model.md)
- [Runtime configuration](docs/configuration.md)
- [Integration architecture](docs/integrations.md)
- [Integration contracts](docs/integration-contracts.md)
- [CRM field mapping](docs/crm-field-mapping.md)

### Agents, orchestration, reliability and security
- [Agent architecture](docs/agent-architecture.md)
- [Prompt strategy](docs/prompt-strategy.md)
- [Model routing](docs/model-routing.md)
- [Workflow orchestration](docs/workflow-orchestration.md)
- [n8n orchestration](docs/n8n-orchestration.md)
- [Reliability architecture](docs/reliability-architecture.md)
- [Security controls](docs/security.md)
- [Recovery runbook](docs/recovery-runbook.md)

### Evaluation, analytics and deployment
- [Evaluation strategy](docs/evaluation-strategy.md)
- [AI release gates](docs/release-gates.md)
- [Operational analytics](docs/operational-analytics.md)
- [Business impact evidence](docs/business-impact.md)
- [Deployment architecture](docs/deployment-architecture.md)
- [SLO evidence model](docs/slo-evidence.md)

### Phase completion records
- [Phase 1](docs/phase-1-completion.md)
- [Phase 2](docs/phase-2-completion.md)
- [Phase 3](docs/phase-3-completion.md)
- [Phase 4](docs/phase-4-completion.md)
- [Phase 5](docs/phase-5-completion.md)
- [Phase 6](docs/phase-6-completion.md)
- [Phase 7](docs/phase-7-completion.md)
- [Phase 8](docs/phase-8-completion.md)

### Key ADRs
- [ADR-005: AI recommends; deterministic policy authorizes](docs/adr/005-ai-recommends-policy-authorizes.md)
- [ADR-007: Workflow state outside agents](docs/adr/007-orchestration-state-outside-agents.md)
- [ADR-008: SQLite restart-safe workflow store](docs/adr/008-sqlite-durable-workflow-store.md)
- [ADR-009: Authenticate webhooks before parsing](docs/adr/009-authenticate-webhooks-before-parsing.md)
- [ADR-010: Separate deterministic and live-model evidence](docs/adr/010-separate-deterministic-and-live-model-evidence.md)
- [ADR-011: Separate measured runtime from business-impact scenarios](docs/adr/011-separate-measured-and-scenario-evidence.md)
- [ADR-012: Keep the SQLite deployment single-replica](docs/adr/012-single-replica-sqlite-deployment-boundary.md)

## Hugging Face publication

- Space: https://huggingface.co/spaces/h0000w/autonomous-revenue-ops
- Dataset: https://huggingface.co/datasets/h0000w/autonomous-revenue-ops
- System/model card: https://huggingface.co/h0000w/autonomous-revenue-ops
- Bucket: https://huggingface.co/buckets/h0000w/autonomous-revenue-ops

GitHub remains the source of truth. The Hugging Face publication workflow uses the repository `HF_TOKEN` secret.

## Current maturity boundary

After Phase 8, this is a **deployment-candidate, contract-tested, restart-safe, security-hardened single-replica AI automation architecture with enforceable deterministic release gates and measured-runtime analytics**.

It is not yet **Production Validated**. Remaining evidence includes reproducible release/supply-chain proof, retained live SaaS/model validation tied to exact commits/configuration, meaningful live deployment observation windows, and shared transactional persistence before any horizontal-replica claim.

Synthetic demonstration values and scenario projections are never presented as customer ROI.

## Author

**Hendarmawan, PhD Eng.**  
Production AI · Agentic Systems · AI Automation · Secure AI Infrastructure

Website: https://hendarmawan.se · GitHub: https://github.com/h00w
