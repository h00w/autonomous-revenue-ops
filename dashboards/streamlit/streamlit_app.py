from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import streamlit as st

APP_TITLE = "Autonomous Revenue Ops · Operations Center"
BASE_URL = os.getenv("ARO_API_BASE_URL", "").rstrip("/")
API_KEY = os.getenv("ARO_API_KEY", "")


def _request(path: str, *, expect_json: bool = True):
    if not BASE_URL:
        raise RuntimeError("ARO_API_BASE_URL is not configured")
    headers = {"Accept": "application/json"}
    if API_KEY:
        headers["X-ARO-API-Key"] = API_KEY
    request = Request(f"{BASE_URL}{path}", headers=headers)
    with urlopen(request, timeout=5) as response:  # nosec B310 - explicit reviewer-configured HTTPS/API target
        payload = response.read().decode("utf-8")
        if expect_json:
            return json.loads(payload)
        return payload


def _safe_fetch(path: str, *, expect_json: bool = True):
    try:
        return _request(path, expect_json=expect_json), None
    except (HTTPError, URLError, TimeoutError, RuntimeError, ValueError) as exc:
        return None, exc.__class__.__name__


st.set_page_config(page_title=APP_TITLE, page_icon="📈", layout="wide")
st.title(APP_TITLE)
st.caption(
    "Reviewer-facing operational evidence for the governed revenue workflow. "
    "This surface never invents customer ROI or production telemetry when no live API is attached."
)

with st.sidebar:
    st.subheader("Proof chain")
    st.markdown("[GitHub source](https://github.com/h00w/autonomous-revenue-ops)")
    st.markdown("[Hugging Face Space](https://huggingface.co/spaces/h0000w/autonomous-revenue-ops)")
    st.markdown("[Evaluation dataset](https://huggingface.co/datasets/h0000w/autonomous-revenue-ops)")
    st.markdown("[System card](https://huggingface.co/h0000w/autonomous-revenue-ops)")
    st.markdown("[Portfolio case study](https://hendarmawan.se/projects/autonomous-revenue-ops/)")
    st.divider()
    st.caption("Runtime target")
    st.code(BASE_URL or "not configured")
    st.caption("API credential")
    st.code("configured" if API_KEY else "not configured")

if not BASE_URL:
    st.info(
        "No live API is configured. Deploy this dashboard with `ARO_API_BASE_URL` pointing to the staging FastAPI service. "
        "If the API requires authentication, add `ARO_API_KEY` as a Streamlit secret/environment variable."
    )
    cols = st.columns(4)
    for col, label, value in zip(
        cols,
        ["Runtime telemetry", "External SaaS calls", "Customer ROI", "Maturity"],
        ["Not attached", "Not executed here", "Not claimed", "Deployment candidate"],
    ):
        col.metric(label, value)
    st.subheader("What the live dashboard will show")
    st.markdown(
        "- persisted workflow status and policy-decision counts\n"
        "- completion, failure, authorization, recovery and human-review ratios\n"
        "- average and P95 recorded workflow lifecycle duration\n"
        "- liveness/readiness state from the deployed API\n"
        "- evidence class returned by the runtime, so measured data remains distinguishable from scenarios"
    )
else:
    live, live_error = _safe_fetch("/health/live")
    ready, ready_error = _safe_fetch("/health/ready")
    summary, summary_error = _safe_fetch("/v1/analytics/summary")

    h1, h2, h3, h4 = st.columns(4)
    h1.metric("Liveness", (live or {}).get("status", "unavailable") if live else "unavailable")
    h2.metric("Readiness", (ready or {}).get("status", "unavailable") if ready else "unavailable")
    h3.metric("Evidence class", (summary or {}).get("evidence_class", "unavailable") if summary else "unavailable")
    h4.metric("Persisted runs", (summary or {}).get("source_run_count", 0) if summary else 0)

    if live_error or ready_error:
        st.warning(f"Health endpoint issue: live={live_error or 'ok'}, ready={ready_error or 'ok'}")

    if summary_error or not summary:
        st.error(
            f"Operational summary unavailable ({summary_error or 'unknown'}). "
            "Check the staging URL and X-ARO-API-Key configuration."
        )
    else:
        if summary.get("evidence_class") != "measured_runtime":
            st.error("Unexpected evidence class. This dashboard only treats `measured_runtime` as operational telemetry.")
        else:
            st.success("Measured runtime evidence is attached to this dashboard.")

        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Completion", f"{summary.get('completion_rate', 0) * 100:.1f}%")
        r2.metric("Failure", f"{summary.get('failure_rate', 0) * 100:.1f}%")
        r3.metric("Human review", f"{summary.get('human_review_rate', 0) * 100:.1f}%")
        r4.metric("Authorization", f"{summary.get('authorization_rate', 0) * 100:.1f}%")

        r5, r6, r7, r8 = st.columns(4)
        r5.metric("Recovery", f"{summary.get('recovery_rate', 0) * 100:.1f}%")
        r6.metric("Execution receipts", f"{summary.get('execution_receipt_rate', 0) * 100:.1f}%")
        r7.metric("Avg lifecycle", f"{summary.get('average_recorded_lifecycle_seconds', 0):.2f}s")
        r8.metric("P95 lifecycle", f"{summary.get('p95_recorded_lifecycle_seconds', 0):.2f}s")

        left, right = st.columns(2)
        with left:
            st.subheader("Workflow states")
            status_counts = summary.get("status_counts", {})
            if status_counts:
                st.bar_chart(status_counts)
            else:
                st.caption("No persisted workflow states yet.")
        with right:
            st.subheader("Policy decisions")
            decision_counts = summary.get("decision_counts", {})
            if decision_counts:
                st.bar_chart(decision_counts)
            else:
                st.caption("No policy decisions persisted yet.")

        with st.expander("Raw aggregate evidence"):
            st.json(summary)

st.divider()
st.subheader("Evidence boundary")
st.markdown(
    "This dashboard is an **operations/reviewer surface**, not an authorization engine. "
    "AI recommendations remain subject to deterministic policy, durable workflow state and bounded adapters in the FastAPI service. "
    "A healthy dashboard does not by itself establish long-window SLO attainment, customer ROI, or full production validation."
)
