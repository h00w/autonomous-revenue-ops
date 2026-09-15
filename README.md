# Autonomous Revenue Ops

> Production-grade AI agents, SaaS integrations, and governed business workflow automation for revenue operations.

[![CI](https://github.com/h00w/autonomous-revenue-ops/actions/workflows/ci.yml/badge.svg)](https://github.com/h00w/autonomous-revenue-ops/actions/workflows/ci.yml)
[![Hugging Face Space](https://img.shields.io/badge/Hugging%20Face-Space-FFD21E?logo=huggingface&logoColor=000)](https://huggingface.co/spaces/h0000w/autonomous-revenue-ops)
[![Dataset](https://img.shields.io/badge/Hugging%20Face-Dataset-FFD21E?logo=huggingface&logoColor=000)](https://huggingface.co/datasets/h0000w/autonomous-revenue-ops)
[![System Card](https://img.shields.io/badge/Hugging%20Face-System%20Card-FFD21E?logo=huggingface&logoColor=000)](https://huggingface.co/h0000w/autonomous-revenue-ops)

**Proof chain:** GitHub source → typed production API → multi-model structured reasoning → deterministic policy → durable workflow state → authenticated ingress → bounded/recoverable execution → dataset-driven release gates → CI evidence artifact → reviewer Space → Hugging Face publication.

## Project phase

| Phase | Status | Evidence |
| --- | --- | --- |
| Phase 0 — Foundation & publication skeleton | ✅ Complete | policy engine, eval dataset, Gradio proof, HF sync |
| Phase 1 — Core production architecture | ✅ Complete | FastAPI, service layer, config, events, correlation, idempotency, structured logs, health checks |
| Phase 2 — Real SaaS & CRM integrations | ✅ Contract-complete · 🔬 live validation pending | HubSpot, Salesforce, Slack, SMTP, webhook adapters; 41/41 tests at merge; benchmark 6/6 |
| Phase 3 — Multi-model AI & agent layer | ✅ Contract-complete · 🔬 live validation pending | OpenAI, Anthropic, Gemini REST adapters; governed Research/Qualification/Outreach agents; 55/55 tests; benchmark 6/6 |
| Phase 4 — Workflow orchestration | ✅ Contract-complete | explicit state machine, idempotent runs, human/research checkpoints, n8n REST/template contracts; 65/65 tests; benchmark 6/6 |
| Phase 5 — Reliability, recovery & security | ✅ Contract-complete | SQLite restart persistence, optimistic revisions, leases/claims, recovery, retry/circuit/DLQ, API auth, signed replay-resistant webhooks; 78/78 tests; benchmark 6/6 |
| Phase 6 — Agent/model evaluation & release gates | ✅ Deterministic release-gate complete · 🔬 live model eval pending | 7-case supervisor evaluation; 100% contract metrics; 0 policy violations; prompt manifest; CI artifact; 82/82 tests; benchmark 6/6 |
| Phase 7 — Operational analytics & business impact | ⏭ Next | telemetry, funnel/intervention/reliability metrics, cost/time accounting, measured-vs-scenario business impact |
| Phases 8–10 | Planned | deployment/SLOs → public proof → live-provider production validation |

The evidence boundary is explicit: Phases 2–6 are implementation- and contract-tested. Phase 5 establishes **restart-safe single-host workflow durability**, not distributed HA. Phase 6's 100% metrics are **deterministic software/governance release-gate evidence**, not live-model quality claims. Live SaaS/model capability validation, production deployment/SLO evidence, and any multi-replica shared-database validation remain required before a final **Production Validated** claim.

## System flow

```text
Inbound lead / signed SaaS webhook / n8n
  → authentication + signature/replay controls
  → FastAPI boundary
  → typed validation + normalization
  → correlation + DB-backed idempotency
  → durable workflow run: RECEIVED → RUNNING
  → multi-model reasoning layer
      ├─ Research Agent
      ├─ Qualification Agent
      └─ controlled provider fallback
  → deterministic policy gate
      ├─ AUTO_ROUTE / NURTURE → READY_FOR_EXECUTION
      ├─ HUMAN_REVIEW → WAITING_HUMAN_REVIEW → approve/reject
      ├─ RESEARCH_MORE → WAITING_RESEARCH → resume with evidence
      └─ BLOCK → COMPLETED without execution
  → Outreach Drafting Agent only when policy authorizes
  → executor lease / execution claim
  → bounded integration execution
      ├─ HubSpot CRM
      ├─ Salesforce CRM
      ├─ Slack
      ├─ SMTP email
      └─ HTTPS webhook
  → bounded retry / circuit breaker / DLQ on normalized failures
  → explicit execution receipt
  → COMPLETED / FAILED
  → persisted recovery evidence

Release path:
  prompt/schema/agent/policy change
  → full regression suite
  → 6/6 policy benchmark
  → 7-case deterministic supervisor release gate
  → prompt ID/version/SHA manifest verification
  → agent-eval-report.json CI artifact
  → merge only when green
```

**AI may propose. Software validates. Policy authorizes. Durable workflow state gates execution. Bounded adapters execute. Explicit evidence determines completion.**

## Production controls implemented so far

| Control | Evidence |
| --- | --- |
| Typed domain/API contracts | `src/models.py` |
| Deterministic authorization | `src/policy.py` |
| Application service | `src/service.py` |
| FastAPI boundary | `src/api.py` |
| Environment/secret configuration | `src/config.py`, `.env.example` |
| Correlation IDs and event envelope | `src/api.py`, `src/models.py` |
| Idempotency semantics | `src/idempotency.py`, `src/orchestration/store.py` |
| Structured JSON logging | `src/logging_config.py` |
| Provider-neutral CRM contract | `src/integrations/crm/base.py` |
| HubSpot CRM v3 | `src/integrations/crm/hubspot.py` |
| Salesforce REST Lead adapter | `src/integrations/crm/salesforce.py` |
| Slack / SMTP / webhook | `src/integrations/notifications/` |
| External error normalization | `src/integrations/http.py`, `src/integrations/errors.py` |
| Multi-model provider contract | `src/ai/base.py` |
| OpenAI / Anthropic / Gemini REST adapters | `src/ai/providers/` |
| Structured-output validation | `src/ai/schema.py`, `src/ai/router.py` |
| Controlled model fallback | `src/ai/router.py` |
| Versioned prompts | `src/ai/prompts.py` |
| Research / Qualification / Outreach agents | `src/ai/agents.py` |
| Deterministic-policy supervisor | `src/ai/supervisor.py` |
| Workflow state machine | `src/orchestration/engine.py`, `src/orchestration/models.py` |
| Restart-safe SQLite workflow store | `src/orchestration/store.py` |
| Optimistic revision / stale-writer protection | `src/orchestration/store.py` |
| Executor and recovery leases | `src/orchestration/store.py`, `src/orchestration/engine.py` |
| Recovery of persisted RUNNING workflows | `src/orchestration/engine.py` |
| Idempotent execution receipts | `src/orchestration/engine.py` |
| Retry / circuit breaker / persistent DLQ | `src/reliability.py` |
| Workflow API authentication | `src/security/auth.py` |
| HMAC webhook verification + replay protection | `src/security/webhooks.py`, `src/security/api.py` |
| Workflow REST API | `src/orchestration/api.py` |
| n8n reference workflow | `n8n/lead-intake.workflow.json` |
| Deterministic agent release dataset | `data/agent_eval_cases.jsonl` — 7 cases / all 5 policy outcomes |
| Agent release gate | `evals/agent_release_gate.py` — all required rates 100%, policy violations 0 |
| Prompt change-control manifest | `evals/prompt_manifest.json` |
| Version-controlled release thresholds | `evals/release_thresholds.json` |
| Opt-in live provider agent evaluation | `evals/live_agent_eval.py` |
| Regression/failure/security/eval tests | `tests/` — 82 passing at Phase 6 merge |
| Policy benchmark | `evals/benchmark.py` — 6/6 |
| SaaS live-validation harness | `scripts/integration_smoke.py` |
| AI-provider validation harness | `scripts/ai_provider_smoke.py` |
| Workflow smoke harness | `scripts/workflow_smoke.py` |
| Reliability/security smoke | `scripts/reliability_smoke.py` — zero network calls |
| CI evidence artifact | `agent-eval-report.json` uploaded by `.github/workflows/ci.yml` |
| HF publication | `.github/workflows/hf-sync.yml` |

## Phase 6 deterministic release metrics

The required CI release gate currently reports:

| Metric | Result |
| --- | ---: |
| Structured-output success | 100% |
| Deterministic decision accuracy | 100% |
| Outreach/authorization agreement | 100% |
| Agent/routing trace integrity | 100% |
| Prompt untrusted-data boundary integrity | 100% |
| Prompt manifest match | yes |
| Policy violations | 0 |
| Evaluation cases | 7 |

These are deterministic contract metrics using the production supervisor with a deterministic structured provider. They are intentionally **not** described as OpenAI, Anthropic, or Gemini accuracy.

## Governed policy demo

Current demonstration thresholds:

- score ≥ 80 and confidence ≥ 0.85, with consent and no risk flags → `AUTO_ROUTE`
- confidence < 0.70 → `RESEARCH_MORE`
- score 60–79 or any risk flag → `HUMAN_REVIEW`
- lower-score valid leads → `NURTURE`
- no contact consent → `BLOCK`

These thresholds demonstrate policy mechanics; they are not claims about a particular customer's sales process.

## Run locally

```bash
git clone https://github.com/h00w/autonomous-revenue-ops.git
cd autonomous-revenue-ops
python -m venv .venv
python -m pip install -r requirements.txt
cp .env.example .env
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

Phase 5+ defaults workflow persistence to `data/workflows.sqlite3`; runtime SQLite/WAL/SHM files, local `.env` files, and locally generated `agent-eval-report.json` are excluded by `.gitignore`.

Endpoints include:

- OpenAPI: `http://localhost:8000/docs`
- Liveness: `GET /health/live`
- Readiness: `GET /health/ready`
- Governed direct evaluation: `POST /v1/leads/evaluate`
- Start/replay workflow: `POST /v1/workflows/leads`
- Inspect workflow: `GET /v1/workflows/runs/{run_id}`
- Human review: `POST /v1/workflows/runs/{run_id}/approval`
- Resume research: `POST /v1/workflows/runs/{run_id}/resume-research`
- Claim authorized execution: `POST /v1/workflows/runs/{run_id}/claim`
- Record execution: `POST /v1/workflows/runs/{run_id}/complete`
- Recover stalled RUNNING workflows: `POST /v1/workflows/recover`
- Signed lead webhook: `POST /v1/webhooks/lead`

## Verify the repository

```bash
make verify
```

CI compiles source/scripts/evals, runs the full regression/failure/security suite, the deterministic policy benchmark, the Phase 6 multi-agent release gate, and every dry-run smoke harness. It also uploads the deterministic agent-evaluation report as build evidence.

## Deterministic vs live evaluation

Run the required deterministic release gate locally:

```bash
python evals/agent_release_gate.py --report agent-eval-report.json
```

Live-provider agent evaluation remains opt-in:

```bash
python evals/live_agent_eval.py openai
python evals/live_agent_eval.py openai --execute --report openai-live-eval.json
```

Without `--execute`, the OpenAI, Anthropic, and Gemini live-eval harnesses make zero external calls. A retained live report must be tied to the exact provider/model, commit, prompts and dataset before it is used as model-quality evidence.

## Live capability validation

Nothing external is contacted unless an opt-in harness is explicitly executed against a dedicated test destination.

```bash
python scripts/integration_smoke.py hubspot
python scripts/ai_provider_smoke.py openai
python scripts/workflow_smoke.py
python scripts/reliability_smoke.py
```

Use `--execute` only where supported and only with dedicated sandbox/test credentials and destinations.

## Documentation

### Core architecture
- [System design](docs/system-design.md)
- [Event / correlation / idempotency](docs/event-model.md)
- [Runtime configuration](docs/configuration.md)
- [Phase 1 completion gates](docs/phase-1-completion.md)

### Integrations
- [Integration architecture](docs/integrations.md)
- [Integration contracts](docs/integration-contracts.md)
- [CRM field mapping](docs/crm-field-mapping.md)
- [Phase 2 completion gates](docs/phase-2-completion.md)

### Multi-model agents
- [Agent architecture](docs/agent-architecture.md)
- [Prompt strategy](docs/prompt-strategy.md)
- [Model routing](docs/model-routing.md)
- [Phase 3 completion gates](docs/phase-3-completion.md)

### Workflow orchestration
- [Workflow state and execution contract](docs/workflow-orchestration.md)
- [n8n orchestration contract](docs/n8n-orchestration.md)
- [Phase 4 completion gates](docs/phase-4-completion.md)

### Reliability & security
- [Reliability architecture](docs/reliability-architecture.md)
- [Security controls](docs/security.md)
- [Recovery runbook](docs/recovery-runbook.md)
- [Phase 5 completion gates](docs/phase-5-completion.md)

### Evaluation & release gates
- [Evaluation strategy](docs/evaluation-strategy.md)
- [AI release gates](docs/release-gates.md)
- [Phase 6 completion gates](docs/phase-6-completion.md)

### ADRs
- [ADR-001: API vs reviewer UI](docs/adr/001-separate-api-from-reviewer-ui.md)
- [ADR-002: Phase 1 idempotency](docs/adr/002-idempotency-phase-1.md)
- [ADR-003: Provider-neutral CRM contract](docs/adr/003-provider-neutral-crm-contract.md)
- [ADR-004: Normalize errors before retries](docs/adr/004-normalize-errors-before-retry-policy.md)
- [ADR-005: AI recommends; deterministic policy authorizes](docs/adr/005-ai-recommends-policy-authorizes.md)
- [ADR-006: Controlled multi-model fallback](docs/adr/006-controlled-model-fallback.md)
- [ADR-007: Workflow state outside agents](docs/adr/007-orchestration-state-outside-agents.md)
- [ADR-008: SQLite restart-safe workflow store](docs/adr/008-sqlite-durable-workflow-store.md)
- [ADR-009: Authenticate webhooks before parsing](docs/adr/009-authenticate-webhooks-before-parsing.md)
- [ADR-010: Separate deterministic and live-model evidence](docs/adr/010-separate-deterministic-and-live-model-evidence.md)

## Hugging Face publication

- Space: https://huggingface.co/spaces/h0000w/autonomous-revenue-ops
- Dataset: https://huggingface.co/datasets/h0000w/autonomous-revenue-ops
- System/model card: https://huggingface.co/h0000w/autonomous-revenue-ops
- Bucket: https://huggingface.co/buckets/h0000w/autonomous-revenue-ops

GitHub is the source of truth. The publication workflow uses the repository `HF_TOKEN` secret.

## Current maturity boundary

After Phase 6, the repository is a **runnable, contract-tested, restart-safe single-host multi-model workflow architecture with enforceable deterministic agent release gates**. It is not yet production validated. SQLite demonstrates transactional persistence and restart recovery on one host, not distributed HA. Phase 6 demonstrates software/governance invariants under deterministic fixtures, not live-provider model accuracy. Remaining proof work includes operational telemetry and measured business-impact evidence, deployable infrastructure/SLO evidence, shared production persistence for any multi-replica topology, and retained live SaaS/model capability validation.

Synthetic demonstration values are never presented as customer ROI.

## Author

**Hendarmawan, PhD Eng.**  
Production AI · Agentic Systems · AI Automation · Secure AI Infrastructure

Website: https://hendarmawan.se · GitHub: https://github.com/h00w
