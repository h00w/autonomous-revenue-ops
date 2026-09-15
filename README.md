# Autonomous Revenue Ops

> Production-grade AI agents, SaaS integrations, and governed business workflow automation for revenue operations.

[![CI](https://github.com/h00w/autonomous-revenue-ops/actions/workflows/ci.yml/badge.svg)](https://github.com/h00w/autonomous-revenue-ops/actions/workflows/ci.yml)
[![Hugging Face Space](https://img.shields.io/badge/Hugging%20Face-Space-FFD21E?logo=huggingface&logoColor=000)](https://huggingface.co/spaces/h0000w/autonomous-revenue-ops)
[![Dataset](https://img.shields.io/badge/Hugging%20Face-Dataset-FFD21E?logo=huggingface&logoColor=000)](https://huggingface.co/datasets/h0000w/autonomous-revenue-ops)
[![System Card](https://img.shields.io/badge/Hugging%20Face-System%20Card-FFD21E?logo=huggingface&logoColor=000)](https://huggingface.co/h0000w/autonomous-revenue-ops)

**Proof chain:** GitHub source → typed production API → deterministic policy → bounded SaaS adapters → regression/evaluation gates → reviewer Space → Hugging Face publication.

## Project phase

| Phase | Status | Evidence |
| --- | --- | --- |
| Phase 0 — Foundation & publication skeleton | ✅ Complete | policy engine, eval dataset, Gradio proof, HF sync |
| Phase 1 — Core production architecture | ✅ Complete | FastAPI, service layer, config, events, correlation, idempotency, structured logs, health checks |
| Phase 2 — Real SaaS & CRM integrations | ✅ Contract-complete · 🔬 live validation pending | HubSpot, Salesforce, Slack, SMTP, webhook adapters; 41/41 tests; benchmark 6/6 |
| Phase 3 — Multi-model AI & agent layer | ⏭ Next | OpenAI, Claude, Gemini, bounded agents, structured outputs |
| Phases 4–10 | Planned | orchestration → reliability/security → evals → analytics → deployment → public proof → production validation |

The evidence boundary is explicit: Phase 2 provider adapters are implemented and contract-tested, but live-account capability validation requires dedicated sandbox/test credentials and remains required before a final **Production Validated** claim.

## System flow

```text
Inbound lead / SaaS webhook / n8n
  → FastAPI boundary
  → typed validation + normalization
  → correlation + idempotency
  → evidence / qualification state
  → deterministic policy gate
      ├─ AUTO_ROUTE
      ├─ HUMAN_REVIEW
      ├─ RESEARCH_MORE
      ├─ NURTURE
      └─ BLOCK
  → bounded integration layer
      ├─ HubSpot CRM
      ├─ Salesforce CRM
      ├─ Slack
      ├─ SMTP email
      └─ HTTPS webhook
  → normalized result / IntegrationError
  → verification / audit / metrics
```

**AI may propose. Software validates. Policy authorizes. Bounded adapters execute. Verification determines completion.**

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
| Provider factories and safe mapping | `src/integrations/factory.py`, `src/integrations/mapping.py` |
| Regression tests | `tests/` — 41 passing at Phase 2 merge |
| Policy benchmark | `evals/benchmark.py` — 6/6 |
| Live validation harness | `scripts/integration_smoke.py` |
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

Endpoints:

- OpenAPI: `http://localhost:8000/docs`
- Liveness: `GET /health/live`
- Readiness: `GET /health/ready`
- Governed lead evaluation: `POST /v1/leads/evaluate`

## Verify the repository

```bash
make verify
```

This compiles source/scripts, runs all tests, executes the policy benchmark, and verifies that each integration smoke command remains side-effect free by default.

## Live sandbox validation

Nothing external is contacted unless `--execute` is explicitly supplied:

```bash
python scripts/integration_smoke.py hubspot
python scripts/integration_smoke.py hubspot --execute
```

Equivalent smoke targets exist for `salesforce`, `slack`, and `smtp`. Use only dedicated sandbox/test destinations.

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

### ADRs
- [ADR-001: API vs reviewer UI](docs/adr/001-separate-api-from-reviewer-ui.md)
- [ADR-002: Phase 1 idempotency](docs/adr/002-idempotency-phase-1.md)
- [ADR-003: Provider-neutral CRM contract](docs/adr/003-provider-neutral-crm-contract.md)
- [ADR-004: Normalize errors before retries](docs/adr/004-normalize-errors-before-retry-policy.md)

## Hugging Face publication

- Space: https://huggingface.co/spaces/h0000w/autonomous-revenue-ops
- Dataset: https://huggingface.co/datasets/h0000w/autonomous-revenue-ops
- System/model card: https://huggingface.co/h0000w/autonomous-revenue-ops
- Bucket: https://huggingface.co/buckets/h0000w/autonomous-revenue-ops

GitHub is the source of truth. The publication workflow uses the repository `HF_TOKEN` secret.

## Current maturity boundary

After Phase 2, the repository is a **runnable, contract-tested production-architecture proof**. It is not yet production validated. Remaining controls include real LLM providers and agents, workflow orchestration, durable recovery/DLQ, webhook security, deeper evaluation, operational telemetry, production deployment/SLO evidence, and live-provider capability evidence.

Synthetic demonstration values are never presented as customer ROI.

## Author

**Hendarmawan, PhD Eng.**  
Production AI · Agentic Systems · AI Automation · Secure AI Infrastructure

Website: https://hendarmawan.se · GitHub: https://github.com/h00w
