from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.ai.prompts import PROMPT_REGISTRY  # noqa: E402
from src.ai.providers.mock import StaticStructuredProvider  # noqa: E402
from src.ai.router import ModelRouter  # noqa: E402
from src.ai.supervisor import RevenueOpsSupervisor  # noqa: E402
from src.models import LeadInput  # noqa: E402

DEFAULT_DATASET = ROOT / "data" / "agent_eval_cases.jsonl"
DEFAULT_THRESHOLDS = ROOT / "evals" / "release_thresholds.json"
DEFAULT_PROMPT_MANIFEST = ROOT / "evals" / "prompt_manifest.json"


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def prompt_manifest_matches(manifest: dict[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    for prompt_id, expected in manifest.items():
        actual = PROMPT_REGISTRY.get(prompt_id)
        if actual is None:
            failures.append(f"missing prompt {prompt_id}")
            continue
        if actual.version != expected["version"]:
            failures.append(f"{prompt_id} version expected={expected['version']} actual={actual.version}")
        digest = _sha256_text(actual.system_prompt)
        if digest != expected["sha256"]:
            failures.append(f"{prompt_id} sha256 changed")
    extra = set(PROMPT_REGISTRY) - set(manifest)
    failures.extend(f"unmanifested prompt {prompt_id}" for prompt_id in sorted(extra))
    return not failures, failures


def _trace_ok(result) -> bool:
    expected_agents = ["research", "qualification"]
    if result.policy.authorized_for_outreach:
        expected_agents.append("outreach")
    if [trace.agent for trace in result.traces] != expected_agents:
        return False
    for trace in result.traces:
        prompt = PROMPT_REGISTRY.get(trace.prompt_id)
        if prompt is None or trace.prompt_version != prompt.version:
            return False
        if trace.provider != "static" or trace.model != "eval-static-v1":
            return False
        if not trace.routing_attempts or not trace.routing_attempts[-1].success:
            return False
    return True


def _request_boundary_ok(provider: StaticStructuredProvider) -> bool:
    if not provider.requests:
        return False
    for request in provider.requests:
        if not request.user_prompt.startswith("<untrusted_data>\n"):
            return False
        if not request.user_prompt.endswith("\n</untrusted_data>"):
            return False
        if "deterministic policy layer" not in request.system_prompt:
            return False
        if request.prompt_id not in PROMPT_REGISTRY:
            return False
        if request.prompt_version != PROMPT_REGISTRY[request.prompt_id].version:
            return False
    return True


def evaluate_cases(cases: list[dict[str, Any]], manifest: dict[str, Any]) -> dict[str, Any]:
    prompt_manifest_match, prompt_manifest_failures = prompt_manifest_matches(manifest)
    rows: list[dict[str, Any]] = []
    structured_success = 0
    decision_correct = 0
    outreach_match = 0
    trace_integrity = 0
    prompt_boundary = 0
    policy_violations = 0

    for case in cases:
        provider = StaticStructuredProvider(
            responses=[case["research"], case["qualification"], case["outreach"]],
            model="eval-static-v1",
        )
        supervisor = RevenueOpsSupervisor(ModelRouter([provider]))
        row: dict[str, Any] = {"case_id": case["case_id"], "expected_decision": case["expected_decision"]}
        try:
            result = supervisor.evaluate(
                LeadInput.model_validate(case["lead"]),
                enrichment_context=case.get("enrichment_context", {}),
                correlation_id=f"eval_{case['case_id']}",
            )
        except Exception as exc:
            row.update({"passed": False, "error": f"{exc.__class__.__name__}: {exc}"})
            rows.append(row)
            continue

        structured_success += 1
        actual_decision = result.policy.decision.value
        decision_ok = actual_decision == case["expected_decision"]
        decision_correct += int(decision_ok)

        actual_outreach = result.outreach is not None
        expected_outreach = bool(case["expect_outreach"])
        outreach_ok = actual_outreach == expected_outreach
        outreach_match += int(outreach_ok)

        violation = actual_outreach and not result.policy.authorized_for_outreach
        policy_violations += int(violation)

        traces_ok = _trace_ok(result)
        trace_integrity += int(traces_ok)
        boundary_ok = _request_boundary_ok(provider)
        prompt_boundary += int(boundary_ok)

        row.update(
            {
                "actual_decision": actual_decision,
                "decision_ok": decision_ok,
                "expected_outreach": expected_outreach,
                "actual_outreach": actual_outreach,
                "outreach_ok": outreach_ok,
                "policy_violation": violation,
                "trace_integrity_ok": traces_ok,
                "prompt_boundary_ok": boundary_ok,
                "provider_calls": provider.calls,
                "passed": decision_ok and outreach_ok and not violation and traces_ok and boundary_ok,
            }
        )
        rows.append(row)

    total = len(cases)
    rate = lambda count: (count / total) if total else 0.0
    metrics = {
        "total_cases": total,
        "structured_output_success_rate": rate(structured_success),
        "decision_accuracy": rate(decision_correct),
        "outreach_authorization_match_rate": rate(outreach_match),
        "trace_integrity_rate": rate(trace_integrity),
        "prompt_boundary_rate": rate(prompt_boundary),
        "policy_violation_count": policy_violations,
        "prompt_manifest_match": prompt_manifest_match,
    }
    return {
        "evidence_class": "deterministic_contract_eval",
        "live_provider_evidence": False,
        "metrics": metrics,
        "prompt_manifest_failures": prompt_manifest_failures,
        "cases": rows,
    }


def apply_thresholds(report: dict[str, Any], thresholds: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    metrics = report["metrics"]
    for name, minimum in thresholds.get("minimums", {}).items():
        if metrics.get(name, 0) < minimum:
            failures.append(f"{name}={metrics.get(name)} below minimum {minimum}")
    for name, maximum in thresholds.get("maximums", {}).items():
        if metrics.get(name, 0) > maximum:
            failures.append(f"{name}={metrics.get(name)} above maximum {maximum}")
    if thresholds.get("require_prompt_manifest_match") and not metrics["prompt_manifest_match"]:
        failures.append("prompt manifest does not match current prompt registry")
    return failures


def run_release_gate(
    dataset_path: Path = DEFAULT_DATASET,
    thresholds_path: Path = DEFAULT_THRESHOLDS,
    prompt_manifest_path: Path = DEFAULT_PROMPT_MANIFEST,
    report_path: Path | None = None,
) -> dict[str, Any]:
    cases = _load_jsonl(dataset_path)
    thresholds = json.loads(thresholds_path.read_text(encoding="utf-8"))
    manifest = json.loads(prompt_manifest_path.read_text(encoding="utf-8"))
    report = evaluate_cases(cases, manifest)
    report["dataset_sha256"] = hashlib.sha256(dataset_path.read_bytes()).hexdigest()
    report["thresholds"] = thresholds
    report["gate_failures"] = apply_thresholds(report, thresholds)
    report["passed"] = not report["gate_failures"]
    if report_path is not None:
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Deterministic Phase 6 agent release gate")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--thresholds", type=Path, default=DEFAULT_THRESHOLDS)
    parser.add_argument("--prompt-manifest", type=Path, default=DEFAULT_PROMPT_MANIFEST)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = run_release_gate(args.dataset, args.thresholds, args.prompt_manifest, args.report)
    print(json.dumps({"evidence_class": report["evidence_class"], "metrics": report["metrics"], "passed": report["passed"], "gate_failures": report["gate_failures"]}, sort_keys=True))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
