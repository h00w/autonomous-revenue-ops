# Reproducibility

This repository implements the **Production AI Evidence Contract v1**.

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

Generated evidence:

```text
evidence/out/current/
├── evidence.json
├── verification.stdout.log
├── verification.stderr.log
├── checksums.sha256
└── summary.md
```

## Interpretation

A reproduction `PASS` means the local non-secret verification chain completed successfully for the recorded commit/environment. It does **not** mean that external provider/SaaS sandbox validation, long-window SLO validation, horizontal scaling, or production deployment has been proven.

The project deliberately keeps those maturity claims separate.

## Clean-room check

```bash
git clone https://github.com/h00w/autonomous-revenue-ops.git
cd autonomous-revenue-ops
git checkout <commit>
python -m pip install -r requirements.txt
make reproduce
cat evidence/out/current/summary.md
```
