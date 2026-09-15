import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_postman_collection_is_secret_free_and_uses_runtime_variables():
    path = ROOT / "postman" / "autonomous-revenue-ops.postman_collection.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw = path.read_text(encoding="utf-8")
    assert payload["info"]["name"] == "Autonomous Revenue Ops"
    assert "{{base_url}}" in raw
    assert "{{aro_api_key}}" in raw
    assert "sk-" not in raw
    assert "Bearer " not in raw


def test_grafana_dashboard_only_references_aggregate_aro_metrics():
    path = ROOT / "observability" / "grafana" / "autonomous-revenue-ops-overview.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    expressions = [
        target["expr"]
        for panel in payload["panels"]
        for target in panel.get("targets", [])
        if "expr" in target
    ]
    assert payload["uid"] == "aro-ops-overview"
    assert expressions
    assert all(expr.startswith("aro_") for expr in expressions)
    assert all("email" not in expr.lower() and "lead_id" not in expr.lower() for expr in expressions)


def test_streamlit_dashboard_has_explicit_evidence_boundary_and_no_embedded_secret():
    path = ROOT / "dashboards" / "streamlit" / "streamlit_app.py"
    text = path.read_text(encoding="utf-8")
    assert "evidence_class" in text
    assert "measured_runtime" in text
    assert "X-ARO-API-Key" in text
    assert "production telemetry when no live API is attached" in text
    assert "sk-" not in text
