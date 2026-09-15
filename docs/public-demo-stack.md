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
| n8n | visual orchestration / execution trace | Blueprint + importable workflow ready | `render.yaml`, `n8n/` |
| [Render staging API](https://autonomous-revenue-ops-staging.onrender.com) | public FastAPI/OpenAPI staging surface | **live** | FastAPI runtime from `main` |
| Grafana Cloud | operational telemetry dashboard | secure scrape contract ready | `observability/grafana/` |
| Postman Public Workspace | forkable API collection | live-staging collection + environment ready | `postman/` |
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

Operational/workflow endpoints are protected by a secret-managed staging key configured in Render and never published in source control. Authenticated clients can use either:

```text
X-ARO-API-Key: <secret>
```

or the standards-compatible form:

```text
Authorization: Bearer <secret>
```

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

## n8n orchestration proof

The root `render.yaml` follows Render's official n8n + Postgres Blueprint architecture and deliberately pins:

```text
docker.io/n8nio/n8n:2.38.7
```

The Frankfurt Render Postgres resource is named:

```text
autonomous-revenue-ops-n8n-db
```

After the Blueprint is applied, import `n8n/lead-intake.workflow.json` and configure an n8n Header Auth credential for `X-ARO-API-Key`. Never place the staging secret in exported workflow JSON.

## Postman public API proof

The collection and staging environment are source-controlled and secret-free:

```text
postman/autonomous-revenue-ops.postman_collection.json
postman/autonomous-revenue-ops-staging.postman_environment.json
```

The default `base_url` is the live Render staging API. `aro_api_key` is intentionally empty and must only be filled in a private/local Postman environment.

## Grafana Cloud direct scrape

Grafana Cloud can use the **Metrics Endpoint** integration directly, without running a separate Prometheus or Alloy collector for this staging proof.

Scrape URL:

```text
https://autonomous-revenue-ops-staging.onrender.com/v1/analytics/metrics
```

Authentication:

```text
Type: Bearer
Token: <the secret-managed staging API key>
```

Grafana Cloud's Metrics Endpoint integration scrapes the target periodically and can then use `observability/grafana/autonomous-revenue-ops-overview.json` as the dashboard definition. The token must be entered only in Grafana Cloud's private connection settings, never committed to GitHub.

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
4. ✅ Protect operational/workflow endpoints with secret-managed API-key and Bearer authentication.
5. 🟡 n8n: pinned Docker/Postgres Blueprint and Frankfurt Postgres are ready; apply the Blueprint, create the n8n owner account, import the workflow and add the private Header Auth credential.
6. 🟡 Postman: staging collection/environment are publication-ready; publish them in a Postman Public Workspace.
7. 🟡 Grafana: direct secure Metrics Endpoint scrape is supported; add the staging scrape job and import the dashboard JSON in Grafana Cloud.
8. ⏭ Run retained live validation against approved sandbox/test model + SaaS providers and the staging deployment; retain the evidence artifacts.
9. ⏭ Publish the guarded `v0.10.0` release/tag and GHCR artifact after the release workflow succeeds.
10. ⏭ Migrate application workflow state from SQLite to PostgreSQL before horizontal-replica production claims.

## Non-negotiable evidence boundary

A public demo link is not production validation. Each surface must say what it proves:

- interactive behavior;
- API contract;
- workflow orchestration;
- measured runtime telemetry;
- deterministic release gating;
- or a specific retained live provider/integration/deployment run.

No synthetic example, dashboard screenshot or short smoke test should be presented as customer ROI or long-window SLO evidence.
