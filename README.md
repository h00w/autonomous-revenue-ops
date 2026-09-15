# Autonomous Revenue Ops

> Production-grade AI agents, SaaS integrations, and governed business workflow automation for revenue operations.

[![CI](https://github.com/h00w/autonomous-revenue-ops/actions/workflows/ci.yml/badge.svg)](https://github.com/h00w/autonomous-revenue-ops/actions/workflows/ci.yml)
[![Hugging Face Space](https://img.shields.io/badge/Hugging%20Face-Space-FFD21E?logo=huggingface&logoColor=000)](https://huggingface.co/spaces/h0000w/autonomous-revenue-ops)
[![Dataset](https://img.shields.io/badge/Hugging%20Face-Dataset-FFD21E?logo=huggingface&logoColor=000)](https://huggingface.co/datasets/h0000w/autonomous-revenue-ops)
[![System Card](https://img.shields.io/badge/Hugging%20Face-System%20Card-FFD21E?logo=huggingface&logoColor=000)](https://huggingface.co/h0000w/autonomous-revenue-ops)

**Proof chain:** GitHub source → typed production API → multi-model structured reasoning → deterministic policy → explicit workflow state → bounded SaaS execution → regression/evaluation gates → reviewer Space → Hugging Face publication.

## Project phase

| Phase | Status | Evidence |
| --- | --- | --- |
| Phase 0 — Foundation & publication skeleton | ✅ Complete | policy engine, eval dataset, Gradio proof, HF sync |
| Phase 1 — Core production architecture | ✅ Complete | FastAPI, service layer, config, events, correlation, idempotency, structured logs, health checks |
| Phase 2 — Real SaaS & CRM integrations | ✅ Contract-complete · 🔬 live validation pending | HubSpot, Salesforce, Slack, SMTP, webhook adapters; 41/41 tests at merge; benchmark 6/6 |
| Phase 3 — Multi-model AI & agent layer | ✅ Contract-complete · 🔬 live validation pending | OpenAI, Anthropic, Gemini REST adapters; governed Research/Qualification/Outreach agents; 55/55 tests; benchmark 6/6 |
| Phase 4 — Workflow orchestration | ✅ Contract-complete · 💾 durable persistence pending | workflow state machine, idempotent runs, approvals/research resume, n8n REST/template contracts; 65/65 tests; benchmark 6/6 |
| Phase 5 — Reliability, recovery & security | ⏭ Next | durable/recoverable execution semantics, retry/circuit breaker/DLQ, webhook/auth controls |
| Phases 6–10 | Planned | evals → analytics → deployment → public proof → production validation |

The evidence boundary is explicit: Phase 2 SaaS adapters, Phase 3 AI-provider adapters, and Phase 4 orchestration semantics are implemented and contract-tested. Live SaaS/model capability validation and durable restart-safe workflow persistence remain required before a final **Production Validated** claim.

## System flow

```text
Inbound lead / SaaS webhook / n8n
  → FastAPI boundary
  → typed validation + normalization
  → correlation + idempotency
  → workflow run: RECEIVED → RUNNING
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
  → bounded integration executor (for example n8n)
      ├─ HubSpot CRM
      ├─ Salesforce CRM
      ├─ Slack
      ├─ SMTP email
      └─ HTTPS webhook
  → explicit execution receipt
  → COMPLETED / FAILED
```

**AI may propose. Software validates. Policy authorizes. Workflow state gates execution. Bounded adapters execute. Explicit evidence determines completion.**

## Production controls implemented so far

| Control | Evidence |
| --- | --- |
| Typed domain/API contracts | `src/models.py` |
| Deterministic authorization | `src/policy.py` |
| Application service | `src/service.py` |
| FastAPI boundary | `src/api.py` |
| Environment/secret configuration | `src/config.py`, `.env.example` |
| Correlation IDs and event envelope | `src/api.py`, `src/models.py` |
| Idempotency semantics | `src/idempotency.py` |
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
| Workflow run-store abstraction | `src/orchestration/store.py` |
| Workflow REST API | `src/orchestration/api.py` |
| n8n reference workflow | `n8n/lead-intake.workflow.json` |
| Regression tests | `tests/` — 65 passing at Phase 4 merge |
| Policy benchmark | `evals/benchmark.py` — 6/6 |
| SaaS live-validation harness | `scripts/integration_smoke.py` |
| AI-provider validation harness | `scripts/ai_provider_smoke.py` |
| Workflow smoke harness | `scripts/workflow_smoke.py` |
| CI | `.github/workflows/ci.yml` |
| HF publication | `.github/workflows/hf-sync.yml` |

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

Endpoints include:

- OpenAPI: `http://localhost:8000/docs`
- Liveness: `GET /health/live`
- Readiness: `GET /health/ready`
- Governed direct evaluation: `POST /v1/leads/evaluate`
- Start/replay workflow: `POST /v1/workflows/leads`
- Inspect workflow: `GET /v1/workflows/runs/{run_id}`
- Human review: `POST /v1/workflows/runs/{run_id}/approval`
- Resume research: `POST /v1/workflows/runs/{run_id}/resume-research`
- Record execution: `POST /v1/workflows/runs/{run_id}/complete`

## Verify the repository

```bash
make verify
```

CI compiles source/scripts, runs the full test suite and policy benchmark, and verifies that SaaS, AI-provider, and workflow smoke commands remain side-effect free by default.

## Live capability validation

Nothing external is contacted unless `--execute` is explicitly supplied.

```bash
python scripts/integration_smoke.py hubspot
python scripts/ai_provider_smoke.py openai
python scripts/workflow_smoke.py
```

Use `--execute` only with dedicated sandbox/test credentials and destinations.

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

### ADRs
- [ADR-001: API vs reviewer UI](docs/adr/001-separate-api-from-reviewer-ui.md)
- [ADR-002: Phase 1 idempotency](docs/adr/002-idempotency-phase-1.md)
- [ADR-003: Provider-neutral CRM contract](docs/adr/003-provider-neutral-crm-contract.md)
- [ADR-004: Normalize errors before retries](docs/adr/004-normalize-errors-before-retry-policy.md)
- [ADR-005: AI recommends; deterministic policy authorizes](docs/adr/005-ai-recommends-policy-authorizes.md)
- [ADR-006: Controlled multi-model fallback](docs/adr/006-controlled-model-fallback.md)
- [ADR-007: Workflow state outside agents](docs/adr/007-orchestration-state-outside-agents.md)

## Hugging Face publication

- Space: https://huggingface.co/spaces/h0000w/autonomous-revenue-ops
- Dataset: https://huggingface.co/datasets/h0000w/autonomous-revenue-ops
- System/model card: https://huggingface.co/h0000w/autonomous-revenue-ops
- Bucket: https://huggingface.co/buckets/h0000w/autonomous-revenue-ops

GitHub is the source of truth. The publication workflow uses the repository `HF_TOKEN` secret.

## Current maturity boundary

After Phase 4, the repository is a **runnable, contract-tested multi-model and workflow-orchestration proof**. It is not yet production validated. The workflow store is process-local, and inbound workflow endpoints do not yet claim production authentication/signature controls. Phase 5 must add recovery, retry/circuit-breaking, dead-letter handling and security hardening; later phases add deeper evals, telemetry, deployment/SLO evidence and live-provider capability evidence.

Synthetic demonstration values are never presented as customer ROI.

## Author

**Hendarmawan, PhD Eng.**  
Production AI · Agentic Systems · AI Automation · Secure AI Infrastructure

Website: https://hendarmawan.se · GitHub: https://github.com/h00w
