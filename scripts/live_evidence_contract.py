from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import Settings  # noqa: E402
from src.evidence.live_validation import (  # noqa: E402
    build_live_validation_evidence,
    runtime_fingerprint,
    verify_live_validation_bundle,
    write_live_validation_bundle,
)


def main() -> None:
    output = ROOT / "live-validation-contract-evidence"
    if output.exists():
        shutil.rmtree(output)

    settings = Settings()
    source_commit = os.getenv("ARO_SOURCE_COMMIT") or os.getenv("GITHUB_SHA")
    evidence = build_live_validation_evidence(
        evidence_class="validation_harness_contract",
        subject={"kind": "contract", "name": "phase-10-live-evidence-harness"},
        executed=False,
        status="dry-run",
        external_calls=0,
        service_version=settings.service_version,
        runtime=runtime_fingerprint(
            environment=settings.environment,
            service_version=settings.service_version,
            subject_kind="contract",
            subject_name="phase-10-live-evidence-harness",
            credential_configured=False,
        ),
        result={
            "network_calls": 0,
            "live_claim_created": False,
            "release_manifest_required_for_live_execution": True,
        },
        root=ROOT,
        source_commit=source_commit,
        dataset_path=ROOT / "data" / "agent_eval_cases.jsonl",
    )
    bundle = write_live_validation_bundle(evidence, output)
    errors = verify_live_validation_bundle(output, root=ROOT)
    report = {
        "evidence_class": "live_validation_contract",
        "passed": not errors,
        "errors": errors,
        "network_calls": 0,
        "bundle_sha256": bundle["evidence_sha256"],
    }
    print(json.dumps(report, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
