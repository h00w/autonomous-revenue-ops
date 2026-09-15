from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "live-validation.yml"


def workflow_text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def test_live_validation_workflow_is_manual_only():
    text = workflow_text()
    assert "workflow_dispatch:" in text
    assert "pull_request:" not in text
    assert "push:" not in text


def test_live_validation_workflow_requires_test_scope_acknowledgement():
    text = workflow_text()
    assert "acknowledge_test_only:" in text
    assert 'test "$ACK" = "true"' in text
    assert 'test "$GITHUB_REF" = "refs/heads/main"' in text


def test_live_validation_workflow_runs_release_binding_before_external_execution():
    text = workflow_text()
    release_index = text.index("python scripts/verify_release_evidence.py release-evidence")
    execution_index = text.index("Execute selected validation and retain evidence")
    assert release_index < execution_index


def test_live_validation_workflow_retains_and_verifies_artifact():
    text = workflow_text()
    assert 'python scripts/verify_live_evidence.py "$EVIDENCE_DIR"' in text
    assert "Upload retained live-validation evidence" in text
    assert "retention-days: 90" in text


def test_live_validation_workflow_caps_deployment_probe_volume():
    text = workflow_text()
    assert 'test "$DEPLOYMENT_REQUESTS" -le 1000' in text
    assert "deployment-probe requires an https:// target" in text
