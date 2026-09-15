# Autonomous Revenue Ops

> Production-grade AI agents, SaaS integrations, and business workflow automation for revenue operations.

[![CI](https://github.com/h00w/autonomous-revenue-ops/actions/workflows/ci.yml/badge.svg)](https://github.com/h00w/autonomous-revenue-ops/actions/workflows/ci.yml)
[![Hugging Face Space](https://img.shields.io/badge/Hugging%20Face-Space-FFD21E?logo=huggingface&logoColor=000)](https://huggingface.co/spaces/h0000w/autonomous-revenue-ops)
[![Dataset](https://img.shields.io/badge/Hugging%20Face-Dataset-FFD21E?logo=huggingface&logoColor=000)](https://huggingface.co/datasets/h0000w/autonomous-revenue-ops)
[![Model Card](https://img.shields.io/badge/Hugging%20Face-Model%20Card-FFD21E?logo=huggingface&logoColor=000)](https://huggingface.co/h0000w/autonomous-revenue-ops)

**Proof chain:** GitHub source → tested policy engine → evaluation dataset → Gradio operations console → Hugging Face publication.

## What this system demonstrates

A realistic revenue-operations workflow that converts an inbound lead into a controlled business action:

```text
Inbound lead
  → validate + normalize
  → deduplicate / idempotency check
  → enrich evidence
  → AI qualification
  → deterministic policy gate
      ├─ AUTO_ROUTE
      ├─ HUMAN_REVIEW
      ├─ RESEARCH_MORE
      └─ NURTURE
  → bounded CRM / messaging adapter
  → verification
  → audit trace + metrics
```

The design intentionally separates **AI recommendation** from **business authorization**. AI can score, classify, summarize, and propose. Deterministic policy decides what is allowed to execute.

## Production controls

| Control | Evidence |
|---|---|
| Typed contracts | `src/models.py` |
| Deterministic authorization | `src/policy.py` |
| Regression tests | `tests/test_policy.py` |
| Evaluation dataset | `data/lead_qualification_eval.jsonl` |
| Interactive proof | `app.py` + Hugging Face Space |
| CI | `.github/workflows/ci.yml` |
| Publication sync | `.github/workflows/hf-sync.yml` |
| Architecture | `docs/architecture.md` |

## Demo decisions

The default rules are deliberately inspectable:

- score ≥ 80 and confidence ≥ 0.85, with consent and no risk flags → `AUTO_ROUTE`
- confidence < 0.70 → `RESEARCH_MORE`
- score 60–79 or any risk flag → `HUMAN_REVIEW`
- lower-score valid leads → `NURTURE`
- no contact consent → outreach is blocked

These thresholds are demo policy, not claims about a specific customer's sales process.

## Hugging Face publication

- **Space:** https://huggingface.co/spaces/h0000w/autonomous-revenue-ops
- **Dataset:** https://huggingface.co/datasets/h0000w/autonomous-revenue-ops
- **Model / system card:** https://huggingface.co/h0000w/autonomous-revenue-ops
- **Bucket:** https://huggingface.co/buckets/h0000w/autonomous-revenue-ops

The repository treats the Hugging Face model page as a **system/model card**, not as a claim that a newly trained foundation model is included. The dataset contains synthetic evaluation cases for policy and qualification behavior. The Space is the interactive reviewer surface.

## Run locally

```bash
git clone https://github.com/h00w/autonomous-revenue-ops.git
cd autonomous-revenue-ops
python -m venv .venv
python -m pip install -r requirements.txt
python -m pytest -q
python app.py
```

Then open the Gradio URL shown in the terminal.

## Business outcome metrics to measure in a real deployment

- automation rate
- manual touches per lead
- mean handling time
- safe escalation rate
- false-automation rate
- duplicate action rate
- CRM/API failure rate
- qualification precision/recall
- cost per completed workflow
- audit completeness

No synthetic demo values are presented as customer ROI.

## Reference design lineage

This project adopts useful workflow patterns seen in public AI-automation portfolios—webhook intake, CRM enrichment, structured AI outputs, deterministic routing, multichannel actions, and human review—while adding production controls such as typed contracts, explicit authorization policy, CI, evaluation data, provenance, and evidence-based maturity claims.

## Author

**Hendarmawan, PhD Eng.**  
Production AI · Agentic Systems · AI Automation · Secure AI Infrastructure

Website: https://hendarmawan.se · GitHub: https://github.com/h00w
