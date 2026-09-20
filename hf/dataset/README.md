---
license: mit
task_categories:
- text-classification
pretty_name: Autonomous Revenue Ops Policy Evaluation
---

# Autonomous Revenue Ops — Evaluation Dataset

Synthetic regression cases for validating deterministic revenue-operations policy behavior.

## Dataset purpose

The dataset checks that structured qualification outputs map to the expected authorized workflow state. It is designed for regression testing, not for training a foundation model.

## Covered behaviors

- high-score, high-confidence autonomous routing
- medium-score human review
- low-confidence evidence collection
- risk-flag override
- consent-based blocking
- lower-score nurture routing

## Schema

Each JSONL row contains:

- `case_id`
- `lead.consent_to_contact`
- `qualification.score`
- `qualification.confidence`
- `qualification.risk_flags`
- `expected_decision`

## Data provenance

All records are synthetic and created for evaluation. They do not contain customer data or real personal data.

## Companion artifacts

- Source: https://github.com/h00w/autonomous-revenue-ops
- Space: https://huggingface.co/spaces/h0000w/autonomous-revenue-ops
- System card: https://huggingface.co/h0000w/autonomous-revenue-ops


## Five-level production-AI proof

This project now reports proof using:

`L1 Runnable → L2 Reproducible → L3 Capability-Validated → L4 Production-Candidate → L5 Production-Validated`.

The GitHub repository computes the level with `make proof`. The public Hugging Face Space, Dataset and system card support the inspectable capability layer, while the project intentionally caps its public claim at **L3 — Capability-Validated** until live CRM operations and target-environment recovery evidence exist.

Specification: https://github.com/h00w/autonomous-revenue-ops/blob/main/PROOF_MODEL.md
