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
| hendarmawan.se | recruiter/client case study + technical article | live | `h00w/h00w.github.io` |
| [Operations Center](https://autonomous-revenue-ops-dashboard.onrender.com) | Streamlit operations/reviewer dashboard | **live** | `dashboards/streamlit/` |
| n8n | visual orchestration / execution trace | importable workflow ready | `n8n/` |
| [Render staging API](https://autonomous-revenue-ops-staging.onrender.com) | public FastAPI/OpenAPI staging surface | **live** | FastAPI runtime from `main` |
| Grafana Cloud | operational telemetry dashboard | dashboard JSON ready | `observability/grafana/` |
| Postman Public Workspace | forkable API collection | collection ready | `postman/` |
| GitHub Releases + GHCR | versioned runtime/release artifacts | workflow ready; v0.10.0 tag publication pending | `.github/workflows/release.yml` |

## Live staging surfaces

### FastAPI staging runtime

Base URL:

```text
https://autonomous-revenue-ops-staging.onrender.com
```

Public reviewer endpoints:

```text
/health/live
/health/ready
/docs
/openapi.json
```

Operational/workflow endpoints are protected by the staging `X-ARO-API-Key` configured in Render and are not published in source control.

Deployment properties currently verified through Render:

- Frankfurt region;
- single application instance;
- Python 3.12.14 pinned explicitly;
- exact source branch `main`;
- automatic deploys enabled;
- source commit for first public staging proof: `e87609d30f430ecfc2d891943c5fbfd3ed0c5a35`.

This is a staging proof, not Production Validated evidence. The current free service also uses ephemeral filesystem storage, so persisted SQLite state is not a durability claim across service replacement/redeploys.

### Streamlit Operations Center

URL:

```text
https://autonomous-revenue-ops-dashboard.onrender.com
```

The dashboard is connected to the staging API with secret-managed environment configuration and reads only:

- `/health/live`;
- `/health/ready`;
- `/v1/analytics/summary`.

The dashboard does not authorize workflow actions and does not invent telemetry when the backend is unavailable.

## Recommended proof path

```text
Portfolio case study
    ↓
GitHub README + architecture
    ↓
Hugging Face interactive demo
    ↓
Live Streamlit Operations Center
    ↓
Live Render FastAPI / OpenAPI staging runtime
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

## Remaining deployment sequence

1. ✅ Publish the portfolio project page and blog article.
2. ✅ Deploy the Streamlit Operations Center and connect it to the staging API.
3. ✅ Deploy the FastAPI application to a public Render staging URL.
4. ✅ Protect operational/workflow endpoints with a secret-managed staging API key.
5. ⏭ Deploy n8n using the recommended official Docker + Render Postgres Blueprint, then import `n8n/lead-intake.workflow.json` and attach Header Auth credentials.
6. ⏭ Publish `postman/autonomous-revenue-ops.postman_collection.json` in a Postman Public Workspace with a secret-free example environment.
7. ⏭ Route `/v1/analytics/metrics` into Prometheus-compatible storage and import the Grafana dashboard JSON.
8. ⏭ Run retained live validation against approved sandbox/test providers and the staging deployment; retain the evidence artifacts.
9. ⏭ Publish the guarded `v0.10.0` release/tag and GHCR artifact after the release workflow succeeds.
10. ⏭ Migrate workflow state from SQLite to PostgreSQL before horizontal-replica production claims.

## n8n deployment boundary

For a persistent public n8n proof, use the official Render n8n architecture: the official n8n Docker image plus Render Postgres. Do not deploy an unpinned ad-hoc npm install or depend on ephemeral SQLite state for the public proof.

The repository already contains the importable governed workflow in `n8n/lead-intake.workflow.json`; n8n remains an orchestration/client layer and never becomes the policy authority.

## Non-negotiable evidence boundary

A public demo link is not production validation. Each surface must say what it proves:

- interactive behavior;
- API contract;
- workflow orchestration;
- measured runtime telemetry;
- deterministic release gating;
- or a specific retained live provider/integration/deployment run.

No synthetic example, dashboard screenshot or short smoke test should be presented as customer ROI or long-window SLO evidence.
