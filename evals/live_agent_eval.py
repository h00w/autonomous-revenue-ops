from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.ai.factory import build_ai_router  # noqa: E402
from src.ai.supervisor import RevenueOpsSupervisor  # noqa: E402
from src.config import Settings  # noqa: E402
from src.models import LeadInput  # noqa: E402

DATASET = ROOT / "data" / "agent_eval_cases.jsonl"


def load_cases() -> list[dict]:
    return [json.loads(line) for line in DATASET.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Opt-in live-provider agent evaluation")
    parser.add_argument("provider", choices=["openai", "anthropic", "gemini"])
    parser.add_argument("--execute", action="store_true", help="Call the configured live/test provider.")
    parser.add_argument("--enforce", action="store_true", help="Exit non-zero when decision accuracy is below 80%.")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    cases = load_cases()

    if not args.execute:
        print(json.dumps({"status": "dry-run", "provider": args.provider, "cases": len(cases), "external_calls": 0, "message": "No model call made. Re-run with --execute using a dedicated API key; live results are separate evidence from the deterministic CI gate."}))
        return

    settings = Settings(ai_provider_order=args.provider)
    router = build_ai_router(settings)
    supervisor = RevenueOpsSupervisor(router)
    rows = []
    correct = 0
    try:
        for case in cases:
            try:
                result = supervisor.evaluate(
                    LeadInput.model_validate(case["lead"]),
                    enrichment_context=case.get("enrichment_context", {}),
                    correlation_id=f"live_eval_{case['case_id']}",
                )
                actual = result.policy.decision.value
                ok = actual == case["expected_decision"]
                correct += int(ok)
                rows.append({"case_id": case["case_id"], "expected": case["expected_decision"], "actual": actual, "decision_ok": ok, "outreach_present": result.outreach is not None, "traces": [trace.model_dump(mode="json") for trace in result.traces]})
            except Exception as exc:
                rows.append({"case_id": case["case_id"], "error": f"{exc.__class__.__name__}: {exc}", "decision_ok": False})
    finally:
        router.close()

    accuracy = correct / len(cases) if cases else 0.0
    report = {"evidence_class": "live_provider_eval", "provider": args.provider, "dataset": str(DATASET.relative_to(ROOT)), "metrics": {"total_cases": len(cases), "decision_accuracy": accuracy}, "cases": rows}
    if args.report:
        args.report.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"evidence_class": "live_provider_eval", "provider": args.provider, "decision_accuracy": accuracy, "cases": len(cases)}))
    if args.enforce and accuracy < 0.8:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
