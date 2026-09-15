# Streamlit Operations Center

This directory contains the reviewer-facing operations surface for Autonomous Revenue Ops.

## Purpose

The dashboard reads aggregate runtime evidence from the FastAPI service and deliberately does not invent telemetry when no live API is connected. It is suitable for Streamlit Community Cloud or another Streamlit-compatible host.

## Deploy

Use `dashboards/streamlit/streamlit_app.py` as the application entrypoint.

Configure:

- `ARO_API_BASE_URL` — HTTPS base URL for the staging API, for example `https://aro-staging.onrender.com`.
- `ARO_API_KEY` — optional value sent as `X-ARO-API-Key` when the staging API has workflow authentication enabled.

Keep the API key in the hosting platform's secret manager. Do not commit it to this repository.

## Runtime endpoints

The dashboard consumes:

- `GET /health/live`
- `GET /health/ready`
- `GET /v1/analytics/summary`

The analytics response is accepted as operational evidence only when it declares `evidence_class=measured_runtime`.

## Evidence boundary

The dashboard is a visualization layer. It does not authorize SaaS execution, change policy decisions, or convert short-lived telemetry into customer ROI or long-window SLO claims.
