# Autonomous Revenue Ops

> Production-grade AI agents, SaaS integrations, and governed business workflow automation for revenue operations.

[![CI](https://github.com/h00w/autonomous-revenue-ops/actions/workflows/ci.yml/badge.svg)](https://github.com/h00w/autonomous-revenue-ops/actions/workflows/ci.yml)
[![Hugging Face Space](https://img.shields.io/badge/Hugging%20Face-Space-FFD21E?logo=huggingface&logoColor=000)](https://huggingface.co/spaces/h0000w/autonomous-revenue-ops)
[![Dataset](https://img.shields.io/badge/Hugging%20Face-Dataset-FFD21E?logo=huggingface&logoColor=000)](https://huggingface.co/datasets/h0000w/autonomous-revenue-ops)
[![Model Card](https://img.shields.io/badge/Hugging%20Face-System%20Card-FFD21E?logo=huggingface&logoColor=000)](https://huggingface.co/h0000w/autonomous-revenue-ops)

**Proof chain:** GitHub source → typed production API → deterministic policy engine → regression/evaluation gates → reviewer Space → Hugging Face publication.

## Project phase

| Phase | Status | Evidence |
| --- | --- | --- |
| Phase 0 — Foundation & publication skeleton | ✅ Complete | policy engine, tests, eval dataset, Gradio proof, HF publication workflow |
| Phase 1 — Core production architecture | 🟡 Implemented / CI-gated | FastAPI, service layer, config, event model, correlation, idempotency, structured logs, health checks |
| Phase 2 — Real SaaS & CRM integrations | ⏭ Next | HubSpot, Salesforce, Slack, email, webhook adapters |
| Phases 3–10 | Planned | see project roadmap / phase documentation |

Phase 1 acceptance criteria are documented in [`docs/phase-1-completion.md`](docs/phase-1-completion.md).

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
  → versioned event envelope
  → bounded integrations (Phase 2+)
  → verification / audit / metrics
```

The design intentionally separates **AI recommendation** from **business authorization**. AI may score, classify, summarize, research and propose. Deterministic software policy decides what may execute.

## Phase 1 production controls

| Control | Evidence |
| --- | --- |
| Typed domain/API contracts | `src/models.py` |
| Deterministic authorization | `src/policy.py` |
| Application service | `src/service.py` |
| FastAPI boundary | `src/api.py` |
| Environment configuration | `src/config.py`, `.env.example` |
| Correlation IDs | API middleware + event envelope |
| Idempotency | `src/idempotency.py` |
| Structured JSON logging | `src/logging_config.py` |
| Liveness/readiness | `/health/live`, `/health/ready` |
| Policy regression tests | `tests/test_policy.py` |
| Service/API tests | `tests/test_service.py`, `tests/test_api.py` |
| Evaluation dataset | `data/lead_qualification_eval.jsonl` |
| Policy benchmark | `evals/benchmark.py` |
| CI | `.github/workflows/ci.yml` |
| HF publication sync | `.github/workflows/hf-sync.yml` |

## Governed demo decisions

The current inspectable policy uses demonstration thresholds:

- score ≥ 80 and confidence ≥ 0.85, with consent and no risk flags → `AUTO_ROUTE`
- confidence < 0.70 → `RESEARCH_MORE`
- score 60–79 or any risk flag → `HUMAN_REVIEW`
- lower-score valid leads → `NURTURE`
- no contact consent → `BLOCK`

These thresholds demonstrate policy mechanics; they are not claims about a particular customer's sales process.

## Run the production API locally

```bash
git clone https://github.com/h00w/autonomous-revenue-ops.git
cd autonomous-revenue-ops
python -m venv .venv
python -m pip install -r requirements.txt
cp .env.example .env
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

Then use:

- OpenAPI/Swagger: `http://localhost:8000/docs`
- Liveness: `GET http://localhost:8000/health/live`
- Readiness: `GET http://localhost:8000/health/ready`
- Governed lead evaluation: `POST http://localhost:8000/v1/leads/evaluate`

See [`docs/configuration.md`](docs/configuration.md) for a complete request example.

## Run the reviewer demo

```bash
python app.py
```

The Gradio surface remains intentionally separate from the production API and is also published as the Hugging Face Space.

## Verify the repository

```bash
make verify
```

Equivalent commands:

```bash
python -m compileall -q src
python -m pytest -q
python evals/benchmark.py
```

## Architecture documentation

- [System design](docs/system-design.md)
- [Event, correlation and idempotency model](docs/event-model.md)
- [Runtime configuration](docs/configuration.md)
- [Phase 1 completion gates](docs/phase-1-completion.md)
- [ADR-001: API vs reviewer UI](docs/adr/001-separate-api-from-reviewer-ui.md)
- [ADR-002: Phase 1 idempotency boundary](docs/adr/002-idempotency-phase-1.md)
- [Original architecture proof](docs/architecture.md)

## Hugging Face publication

- **Space:** https://huggingface.co/spaces/h0000w/autonomous-revenue-ops
- **Dataset:** https://huggingface.co/datasets/h0000w/autonomous-revenue-ops
- **System/model card:** https://huggingface.co/h0000w/autonomous-revenue-ops
- **Bucket:** https://huggingface.co/buckets/h0000w/autonomous-revenue-ops

GitHub is the source of truth. `.github/workflows/hf-sync.yml` publishes the reviewer Space, evaluation dataset and system card through the repository `HF_TOKEN` secret.

## Current maturity boundary

After Phase 1 this repository is intended to qualify as a **runnable production-architecture proof**, not yet a production-validated service. The current idempotency store is process-local; live CRM providers, auth/signature validation, distributed recovery, persistent DLQ/replay, production SLO evidence and real deployment infrastructure are introduced in later phases.

## Business metrics for real deployments

The architecture is designed to measure automation rate, manual touches per lead, mean handling time, safe escalation rate, false-automation rate, duplicate action rate, CRM/API failure rate, qualification precision/recall, cost per completed workflow and audit completeness.

Synthetic demo values are never presented as customer ROI.

## Author

**Hendarmawan, PhD Eng.**  
Production AI · Agentic Systems · AI Automation · Secure AI Infrastructure

Website: https://hendarmawan.se · GitHub: https://github.com/h00w
