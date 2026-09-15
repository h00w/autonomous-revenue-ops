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
from src.evidence.live_validation import (  # noqa: E402
    build_live_validation_evidence,
    runtime_fingerprint,
    utc_now,
    validate_release_binding,
    write_live_validation_bundle,
)
from src.models import LeadInput  # noqa: E402

DATASET = ROOT / "data" / "agent_eval_cases.jsonl"


def load_cases() -> list[dict]:
    return [json.loads(line) for line in DATASET.read_text(encoding="utf-8").splitlines() if line.strip()]


def _secret_configured(value) -> bool:
    if value is None:
        return False
    getter = getattr(value, "get_secret_value", None)
    raw = getter() if callable(getter) else str(value)
    return bool(raw.strip())


def _provider_runtime(settings: Settings, provider: str) -> dict:
    model = getattr(settings, f"{provider}_model")
    base_url = getattr(settings, f"{provider}_base_url")
    credential = getattr(settings, f"{provider}_api_key")
    return runtime_fingerprint(
        environment=settings.environment,
        service_version=settings.service_version,
        subject_kind="model",
        subject_name=provider,
        model=model,
        target_url=base_url,
        credential_configured=_secret_configured(credential),
        extra={"ai_timeout_seconds": settings.ai_timeout_seconds},
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Opt-in live-provider agent evaluation")
    parser.add_argument("provider", choices=["openai", "anthropic", "gemini"])
    parser.add_argument("--execute", action="store_true", help="Call the configured live/test provider.")
    parser.add_argument("--enforce", action="store_true", help="Exit non-zero when decision accuracy is below 80%.")
    parser.add_argument("--report", type=Path, help="Optional human-readable copy of the retained evidence JSON.")
    parser.add_argument("--evidence-dir", type=Path, help="Required for executed live validation.")
    parser.add_argument("--release-manifest", type=Path, default=Path("release-evidence/manifest.json"))
    args = parser.parse_args()
    cases = load_cases()

    if not args.execute:
        print(
            json.dumps(
                {
                    "status": "dry-run",
                    "provider": args.provider,
                    "cases": len(cases),
                    "external_calls": 0,
                    "message": "No model call made. Re-run with --execute and --evidence-dir using a dedicated API key; live results remain separate from the deterministic CI gate.",
                }
            )
        )
        return

    if args.evidence_dir is None:
        raise SystemExit("--evidence-dir is required with --execute so live results are retained and verifiable")

    settings = Settings(ai_provider_order=args.provider)
    validate_release_binding(
        service_version=settings.service_version,
        root=ROOT,
        release_manifest=args.release_manifest,
    )
    credential = getattr(settings, f"{args.provider}_api_key")
    if not _secret_configured(credential):
        raise SystemExit(f"A non-empty {args.provider} API credential is required before live evaluation")

    router = build_ai_router(settings)
    supervisor = RevenueOpsSupervisor(router)
    rows = []
    correct = 0
    observed_calls = 0
    started_at = utc_now()
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
                traces = [trace.model_dump(mode="json") for trace in result.traces]
                observed_calls += max(1, len(traces))
                rows.append(
                    {
                        "case_id": case["case_id"],
                        "expected": case["expected_decision"],
                        "actual": actual,
                        "decision_ok": ok,
                        "outreach_present": result.outreach is not None,
                        "traces": traces,
                    }
                )
            except Exception as exc:
                observed_calls += 1
                rows.append(
                    {
                        "case_id": case["case_id"],
                        "error_class": exc.__class__.__name__,
                        "decision_ok": False,
                    }
                )
    finally:
        router.close()
    finished_at = utc_now()

    accuracy = correct / len(cases) if cases else 0.0
    result_payload = {
        "metrics": {
            "total_cases": len(cases),
            "decision_accuracy": accuracy,
            "successful_decisions": correct,
        },
        "cases": rows,
    }
    evidence = build_live_validation_evidence(
        evidence_class="live_provider_eval",
        subject={
            "kind": "model",
            "name": args.provider,
            "configured_model": getattr(settings, f"{args.provider}_model"),
        },
        executed=True,
        status="success" if correct == len(cases) else "completed_with_mismatches",
        external_calls=observed_calls,
        service_version=settings.service_version,
        runtime=_provider_runtime(settings, args.provider),
        result=result_payload,
        root=ROOT,
        dataset_path=DATASET,
        release_manifest=args.release_manifest,
        started_at=started_at,
        finished_at=finished_at,
    )
    bundle = write_live_validation_bundle(evidence, args.evidence_dir)
    if args.report:
        args.report.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "evidence_class": "live_provider_eval",
                "provider": args.provider,
                "decision_accuracy": accuracy,
                "cases": len(cases),
                "external_calls_observed": observed_calls,
                "bundle": bundle,
            },
            sort_keys=True,
        )
    )
    if args.enforce and accuracy < 0.8:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
