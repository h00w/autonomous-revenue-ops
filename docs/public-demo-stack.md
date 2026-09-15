# Public Demo & Distribution Stack

Autonomous Revenue Ops uses multiple public surfaces because no single host proves every engineering property well.

## Publication architecture

| Surface | Role | Status | Source of truth |
| --- | --- | --- | --- |
| GitHub | canonical source, CI, release evidence, ADRs | live | this repository |
| Hugging Face Space | interactive policy/system demonstration | live | `app.py`, HF publication workflow |
| Hugging Face Dataset | evaluation/regression data | live | repository data/evals |
| Hugging Face system card | intended use, limitations, evidence boundary | live | `hf/model/README.md` |
| Hugging Face Bucket | auxiliary public artifact storage | live | publication artifacts |
| hendarmawan.se | recruiter/client case study | publication layer | `h00w/h00w.github.io` |
| Streamlit Community Cloud | operations/reviewer dashboard | source ready; deployment pending | `dashboards/streamlit/` |
| n8n | visual orchestration / execution trace | importable workflow ready | `n8n/` |
| Render | public staging FastAPI + OpenAPI surface | deployment pending | Docker/FastAPI runtime |
| Grafana Cloud | operational telemetry dashboard | dashboard JSON ready | `observability/grafana/` |
| Postman Public Workspace | forkable API collection | collection ready | `postman/` |
| GitHub Releases + GHCR | versioned runtime/release artifacts | workflow ready; v0.10.0 tag publication pending | `.github/workflows/release.yml` |

## Recommended proof path

```text
Portfolio case study
    ↓
GitHub README + architecture
    ↓
Hugging Face interactive demo
    ↓
Streamlit Operations Center
    ↓
n8n visual workflow
    ↓
Postman API collection
    ↓
Grafana runtime telemetry
    ↓
CI / release evidence / retained live-validation artifacts
```

A reviewer should be able to understand the business problem in under 30 seconds and reach inspectable engineering evidence in under two minutes.

## Deployment sequence

1. Publish the portfolio project page and blog article.
2. Deploy the Streamlit Operations Center from `dashboards/streamlit/streamlit_app.py`.
3. Deploy the Docker/FastAPI service to a staging URL (Render is a suitable simple public staging target).
4. Attach the Streamlit dashboard to the staging URL using secret-managed `ARO_API_KEY`.
5. Import `n8n/lead-intake.workflow.json` into n8n and attach a Header Auth credential rather than embedding secrets.
6. Publish `postman/autonomous-revenue-ops.postman_collection.json` in a Postman Public Workspace with a secret-free example environment.
7. Route `/v1/analytics/metrics` into Prometheus-compatible storage and import the Grafana dashboard JSON.
8. Run retained live validation against approved sandbox/test providers and retain the evidence artifacts.
9. Publish the guarded `v0.10.0` release/tag and container artifact after the release workflow succeeds.

## Non-negotiable evidence boundary

A public demo link is not production validation. Each surface must say what it proves:

- interactive behavior;
- API contract;
- workflow orchestration;
- measured runtime telemetry;
- deterministic release gating;
- or a specific retained live provider/integration/deployment run.

No synthetic example, dashboard screenshot or short smoke test should be presented as customer ROI or long-window SLO evidence.
