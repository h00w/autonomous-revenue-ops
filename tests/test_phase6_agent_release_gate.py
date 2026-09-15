import json
from pathlib import Path

from evals.agent_release_gate import (
    DEFAULT_DATASET,
    DEFAULT_PROMPT_MANIFEST,
    prompt_manifest_matches,
    run_release_gate,
)


def test_deterministic_agent_release_gate_passes_and_writes_report(tmp_path):
    report_path = tmp_path / "report.json"
    report = run_release_gate(report_path=report_path)
    assert report["passed"] is True
    assert report["evidence_class"] == "deterministic_contract_eval"
    assert report["live_provider_evidence"] is False
    assert report["metrics"]["structured_output_success_rate"] == 1.0
    assert report["metrics"]["decision_accuracy"] == 1.0
    assert report["metrics"]["outreach_authorization_match_rate"] == 1.0
    assert report["metrics"]["trace_integrity_rate"] == 1.0
    assert report["metrics"]["prompt_boundary_rate"] == 1.0
    assert report["metrics"]["policy_violation_count"] == 0
    assert report_path.exists()
    stored = json.loads(report_path.read_text(encoding="utf-8"))
    assert stored["passed"] is True


def test_agent_eval_dataset_covers_all_policy_decisions_and_injection_boundary_case():
    cases = [json.loads(line) for line in DEFAULT_DATASET.read_text(encoding="utf-8").splitlines() if line.strip()]
    decisions = {case["expected_decision"] for case in cases}
    assert decisions == {"AUTO_ROUTE", "HUMAN_REVIEW", "RESEARCH_MORE", "NURTURE", "BLOCK"}
    injection = next(case for case in cases if case["case_id"] == "prompt_injection_untrusted_data")
    assert "IGNORE ALL PREVIOUS INSTRUCTIONS" in injection["lead"]["message"]
    assert injection["expected_decision"] == "HUMAN_REVIEW"


def test_prompt_manifest_matches_registry():
    manifest = json.loads(DEFAULT_PROMPT_MANIFEST.read_text(encoding="utf-8"))
    ok, failures = prompt_manifest_matches(manifest)
    assert ok is True
    assert failures == []


def test_prompt_manifest_detects_unreviewed_prompt_change():
    manifest = json.loads(DEFAULT_PROMPT_MANIFEST.read_text(encoding="utf-8"))
    manifest["revenue_ops.research"]["sha256"] = "0" * 64
    ok, failures = prompt_manifest_matches(manifest)
    assert ok is False
    assert any("sha256 changed" in failure for failure in failures)
