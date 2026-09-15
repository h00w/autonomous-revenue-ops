import json
from pathlib import Path


def test_n8n_lead_intake_template_is_parseable_and_forwards_governance_headers():
    path = Path("n8n/lead-intake.workflow.json")
    workflow = json.loads(path.read_text())

    assert workflow["active"] is False
    nodes = {node["name"]: node for node in workflow["nodes"]}
    assert {"Lead Webhook", "Start Governed Workflow", "Respond to Webhook"} <= set(nodes)

    start = nodes["Start Governed Workflow"]
    assert start["type"] == "n8n-nodes-base.httpRequest"
    assert "/v1/workflows/leads" in start["parameters"]["url"]
    headers = {
        item["name"]: item["value"]
        for item in start["parameters"]["headerParameters"]["parameters"]
    }
    assert "Idempotency-Key" in headers
    assert "X-Correlation-ID" in headers
    assert "credentials" not in json.dumps(workflow).lower()
