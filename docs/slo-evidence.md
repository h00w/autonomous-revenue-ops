# SLO evidence model

Phase 8 separates an SLO **target** from evidence that a deployed system actually meets it.

## Candidate targets

The repository baseline is intentionally labeled `candidate_slo_target`:

- liveness availability: >= 99.5%;
- readiness success: >= 99.5%;
- p95 health-probe latency: <= 500 ms.

These are engineering release targets for this portfolio system, not customer commitments.

## Evidence classes

`candidate_slo_target` contains only the configured target. `container_runtime_smoke` proves a locally built container can boot and answer health checks under hardened runtime flags. `live_deployment_probe` is emitted only when `scripts/slo_probe.py --execute` contacts an explicitly selected deployment.

CI runs `scripts/slo_probe.py` without `--execute`, so CI never turns synthetic/local data into a live-deployment SLO claim.

## Live probe

Example against a dedicated staging endpoint:

```bash
python scripts/slo_probe.py \
  --base-url https://staging.example.com \
  --requests 100 \
  --execute \
  --enforce
```

A short probe is useful capability evidence but is not a substitute for a statistically meaningful production observation window, alert history, incident history, or error-budget reporting.
