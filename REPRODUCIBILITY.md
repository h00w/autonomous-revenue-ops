# Reproducibility

This repository implements **Production AI Evidence Contract v1** and the **Production AI Five-Level Proof Model v1**.

## Prerequisites

- Git
- Python 3.12+
- GNU Make

Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Reproduce

```bash
make reproduce
```

The reproduction command runs the repository's existing deterministic `make verify` chain, then binds the result to source, environment, dependency, benchmark, policy and integration-artifact digests.

Generated evidence is written to `evidence/out/current/` with `evidence.json`, retained verification logs, `checksums.sha256`, and `summary.md`.

A reproduction `PASS` is **L2 — Reproducible**. It does **not** mean that external provider/SaaS sandbox validation, long-window SLO validation, horizontal scaling, or production deployment has been proven.

## Assess the five-level proof

```bash
make proof
```

The proof assessor verifies the public Hugging Face Space, Dataset, and system card in addition to the Level-2 evidence and emits `proof.json` plus `proof-summary.md`.

The current public portfolio proof is deliberately capped at **L3 — Capability-Validated** because the Hugging Face assets and regression/policy evidence are inspectable, while the published system card still describes synthetic inputs and simulated external side effects. Live CRM production outcomes are not promoted into the proof claim.

For a network-independent run:

```bash
make proof-offline
```

Offline assessment can establish at most L2.

See [PROOF_MODEL.md](PROOF_MODEL.md) for all five cumulative levels.

## Clean-room check

```bash
git clone https://github.com/h00w/autonomous-revenue-ops.git
cd autonomous-revenue-ops
git checkout <commit>
python -m pip install -r requirements.txt
make proof
cat evidence/out/current/proof-summary.md
```
