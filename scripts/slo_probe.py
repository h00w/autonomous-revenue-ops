from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import Settings  # noqa: E402
from src.evidence.live_validation import (  # noqa: E402
    build_live_validation_evidence,
    runtime_fingerprint,
    sanitize_url,
    utc_now,
    write_live_validation_bundle,
)
from src.operations.slo import ProbeSample, SLOTargets, evaluate_slo  # noqa: E402


def _probe(url: str, timeout: float) -> tuple[bool, float]:
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            ok = 200 <= response.status < 300
            response.read()
    except (urllib.error.URLError, TimeoutError, OSError):
        ok = False
    return ok, (time.perf_counter() - started) * 1000.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--target-label", default="selected-deployment")
    parser.add_argument("--requests", type=int, default=20)
    parser.add_argument("--timeout", type=float, default=2.0)
    parser.add_argument("--interval", type=float, default=0.1)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--enforce", action="store_true")
    parser.add_argument("--evidence-dir", type=Path, help="Required with --execute.")
    parser.add_argument("--release-manifest", type=Path, default=Path("release-evidence/manifest.json"))
    args = parser.parse_args()

    targets = SLOTargets()
    if not args.execute:
        print(
            json.dumps(
                {
                    "status": "dry-run",
                    "evidence_class": "candidate_slo_target",
                    "external_calls": 0,
                    "targets": targets.model_dump(),
                    "message": "No deployment probe made. Use --execute and --evidence-dir only against an explicitly selected deployment.",
                },
                sort_keys=True,
            )
        )
        return

    if args.evidence_dir is None:
        raise SystemExit("--evidence-dir is required with --execute so deployment observations are retained")
    if args.requests < 1:
        raise SystemExit("--requests must be at least 1")

    settings = Settings()
    samples: list[ProbeSample] = []
    started_at = utc_now()
    for index in range(args.requests):
        live_ok, live_ms = _probe(args.base_url.rstrip("/") + "/health/live", args.timeout)
        ready_ok, ready_ms = _probe(args.base_url.rstrip("/") + "/health/ready", args.timeout)
        samples.append(
            ProbeSample(
                live_ok=live_ok,
                ready_ok=ready_ok,
                live_latency_ms=live_ms,
                ready_latency_ms=ready_ms,
            )
        )
        if index + 1 < args.requests and args.interval > 0:
            time.sleep(args.interval)

    report = evaluate_slo(samples, targets)
    evidence = build_live_validation_evidence(
        evidence_class="live_deployment_probe",
        subject={
            "kind": "deployment",
            "name": args.target_label,
            "target": sanitize_url(args.base_url),
        },
        executed=True,
        status="passed" if report.passed else "failed_target",
        external_calls=args.requests * 2,
        service_version=settings.service_version,
        runtime=runtime_fingerprint(
            environment=settings.environment,
            service_version=settings.service_version,
            subject_kind="deployment",
            subject_name=args.target_label,
            target_url=args.base_url,
            credential_configured=None,
            extra={
                "requests": args.requests,
                "timeout_seconds": args.timeout,
                "interval_seconds": args.interval,
            },
        ),
        result={
            "slo_report": report.model_dump(mode="json"),
            "targets": targets.model_dump(mode="json"),
            "observation_count": len(samples),
        },
        root=ROOT,
        release_manifest=args.release_manifest,
        started_at=started_at,
        finished_at=utc_now(),
    )
    bundle = write_live_validation_bundle(evidence, args.evidence_dir)
    print(
        json.dumps(
            {
                "evidence_class": "live_deployment_probe",
                "passed": report.passed,
                "external_calls": args.requests * 2,
                "bundle": bundle,
            },
            sort_keys=True,
        )
    )
    if args.enforce and not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
