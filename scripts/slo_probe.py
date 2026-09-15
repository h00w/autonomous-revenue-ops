from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request

from src.operations.slo import ProbeSample, SLOTargets, evaluate_slo


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
    parser.add_argument("--requests", type=int, default=20)
    parser.add_argument("--timeout", type=float, default=2.0)
    parser.add_argument("--interval", type=float, default=0.1)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--enforce", action="store_true")
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
                    "message": "No deployment probe made. Use --execute only against an explicitly selected deployment.",
                },
                sort_keys=True,
            )
        )
        return

    samples: list[ProbeSample] = []
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
    print(report.model_dump_json())
    if args.enforce and not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
