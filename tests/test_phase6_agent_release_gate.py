import json
import pytest
from pathlib import Path


from evals.agent_release_gate import (
    DEFAULT_DATASET,
    DEFAULT_PROMPT_MANIFEST,
    prompt_manifest_matches,
    run_release_gate,
    apply_thresholds,
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


def test_duplicate_cases_cannot_inflate_release_evidence(tmp_path):
    first = next(line for line in DEFAULT_DATASET.read_text().splitlines() if line.strip())
    dataset = tmp_path / "cases.jsonl"
    dataset.write_text(DEFAULT_DATASET.read_text() + "\n" + first + "\n")
    report = run_release_gate(dataset_path=dataset)
    assert not report["passed"]
    assert "dataset contains duplicate case IDs" in report["gate_failures"]


@pytest.mark.parametrize("invalid", ["true", "false", 1, 0, None, [], {}])
def test_outreach_expectations_require_boolean_labels(tmp_path, invalid):
    cases = [json.loads(line) for line in DEFAULT_DATASET.read_text().splitlines() if line.strip()]
    cases[0]["expect_outreach"] = invalid
    dataset = tmp_path / "cases.jsonl"
    dataset.write_text("\n".join(json.dumps(case) for case in cases))
    report = run_release_gate(dataset_path=dataset)
    assert report["passed"] is False
    assert any("expect_outreach must be a boolean" in failure for failure in report["gate_failures"])


def test_invalid_threshold_does_not_pass_open():
    report = {"metrics": {"total_cases": 1, "decision_accuracy": 1.0, "prompt_manifest_match": True}}
    assert apply_thresholds(report, {})
    assert apply_thresholds(report, {"minimums": {}})
    assert apply_thresholds(report, {"minimums": []})
    assert apply_thresholds(report, {"minimums": {"decision_accuracy": float("nan")}})
    assert apply_thresholds(report, {"minimums": {"unknown_metric": 0}})
    assert apply_thresholds(report, {"minimums": {"decision_accuracy": -1}})
    assert apply_thresholds(report, {"minimums": {"decision_accuracy": 2}})
    assert apply_thresholds(report, {"maximums": {"decision_accuracy": True}})


@pytest.mark.parametrize("value", [float("nan"), float("inf"), True, "1", -1, 2, None])
def test_invalid_report_accuracy_cannot_pass(value):
    assert apply_thresholds({"metrics": {"total_cases": 1, "decision_accuracy": value}}, {"minimums": {"decision_accuracy": 0.9}})


def test_nonfinite_policy_violation_count_cannot_pass():
    assert apply_thresholds({"metrics": {"total_cases": 1, "policy_violation_count": float("nan")}}, {"maximums": {"policy_violation_count": 0}})


@pytest.mark.parametrize("total", [0, -1, True, 1.5, "1", None])
def test_release_gate_rejects_unmeasured_or_malformed_sample_counts(total):
    report = {"metrics": {"total_cases": total, "decision_accuracy": 1.0}}
    assert apply_thresholds(report, {"minimums": {"decision_accuracy": 0.9}})


def test_manifest_flags_cannot_disable_or_spoof_binding_checks():
    metrics = {"total_cases": 1, "decision_accuracy": 1.0, "prompt_manifest_match": True}
    policy = {"minimums": {"decision_accuracy": 0.9}, "require_prompt_manifest_match": True}
    assert apply_thresholds({"metrics": metrics}, policy) == []
    for invalid in ("false", 0, [], None):
        assert apply_thresholds({"metrics": metrics}, dict(policy, require_prompt_manifest_match=invalid))
        assert apply_thresholds({"metrics": dict(metrics, prompt_manifest_match=invalid)}, policy)
