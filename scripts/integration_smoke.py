"""Opt-in live integration smoke test with retained evidence.

This script never executes external side effects unless --execute is supplied.
Executed checks require an evidence directory and a matching release manifest.
Use sandbox/test accounts and destinations only, never production customer records.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import Settings  # noqa: E402
from src.evidence.live_validation import (  # noqa: E402
    build_live_validation_evidence,
    fingerprint_identifier,
    runtime_fingerprint,
    utc_now,
    write_live_validation_bundle,
)
from src.integrations.factory import (  # noqa: E402
    build_crm_adapter,
    build_slack_notifier,
    build_smtp_adapter,
)
from src.integrations.models import CRMLeadRecord, EmailMessage  # noqa: E402


def smoke_record() -> CRMLeadRecord:
    email = os.getenv("ARO_SMOKE_EMAIL", "aro-smoke@example.com")
    return CRMLeadRecord(
        external_key=os.getenv("ARO_SMOKE_EXTERNAL_KEY", "aro_phase10_smoke"),
        email=email,
        first_name=os.getenv("ARO_SMOKE_FIRST_NAME", "ARO"),
        last_name=os.getenv("ARO_SMOKE_LAST_NAME", "SmokeTest"),
        company=os.getenv("ARO_SMOKE_COMPANY", "Autonomous Revenue Ops Test"),
        title="Integration Smoke Test",
        source="Other",
    )


def _runtime(settings: Settings, provider: str) -> dict:
    if provider == "hubspot":
        return runtime_fingerprint(
            environment=settings.environment,
            service_version=settings.service_version,
            subject_kind="integration",
            subject_name=provider,
            target_url=settings.hubspot_base_url,
            credential_configured=settings.hubspot_access_token is not None,
        )
    if provider == "salesforce":
        return runtime_fingerprint(
            environment=settings.environment,
            service_version=settings.service_version,
            subject_kind="integration",
            subject_name=provider,
            target_url=settings.salesforce_instance_url,
            credential_configured=settings.salesforce_access_token is not None,
            extra={"api_root": settings.salesforce_api_root},
        )
    if provider == "slack":
        return runtime_fingerprint(
            environment=settings.environment,
            service_version=settings.service_version,
            subject_kind="integration",
            subject_name=provider,
            credential_configured=settings.slack_webhook_url is not None,
        )
    smtp_target = f"smtp://{settings.smtp_host}:{settings.smtp_port}" if settings.smtp_host else None
    return runtime_fingerprint(
        environment=settings.environment,
        service_version=settings.service_version,
        subject_kind="integration",
        subject_name=provider,
        target_url=smtp_target,
        credential_configured=bool(settings.smtp_username or settings.smtp_password),
        extra={"starttls": settings.smtp_use_starttls},
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("provider", choices=["hubspot", "salesforce", "slack", "smtp"])
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually call the configured external sandbox/test service.",
    )
    parser.add_argument("--evidence-dir", type=Path, help="Required with --execute.")
    parser.add_argument("--release-manifest", type=Path, default=Path("release-evidence/manifest.json"))
    args = parser.parse_args()
    settings = Settings()

    if not args.execute:
        print(
            json.dumps(
                {
                    "status": "dry-run",
                    "provider": args.provider,
                    "external_calls": 0,
                    "message": "No external call made. Re-run with --execute and --evidence-dir after configuring sandbox/test credentials.",
                }
            )
        )
        return

    if args.evidence_dir is None:
        raise SystemExit("--evidence-dir is required with --execute so the side effect is retained as verifiable evidence")

    started_at = utc_now()
    result_payload: dict
    if args.provider in {"hubspot", "salesforce"}:
        adapter = build_crm_adapter(settings, args.provider)
        try:
            result = adapter.upsert_lead(smoke_record())
        finally:
            adapter.close()
        result_payload = {
            "provider": result.provider,
            "record_id_sha256": fingerprint_identifier(result.record_id),
            "created": result.created,
            "updated": result.updated,
        }
    elif args.provider == "slack":
        notifier = build_slack_notifier(settings)
        try:
            result = notifier.send("Autonomous Revenue Ops Phase 10 retained integration smoke test")
        finally:
            notifier.close()
        result_payload = {"provider": result.provider, "delivered": result.delivered}
    else:
        adapter = build_smtp_adapter(settings)
        result = adapter.send(
            EmailMessage(
                to=os.getenv("ARO_SMOKE_EMAIL", "aro-smoke@example.com"),
                subject="Autonomous Revenue Ops Phase 10 retained smoke test",
                text="Explicit sandbox/test integration smoke from the retained live-validation harness.",
            )
        )
        result_payload = {"provider": result.provider, "delivered": result.delivered}

    evidence = build_live_validation_evidence(
        evidence_class="live_integration_smoke",
        subject={"kind": "integration", "name": args.provider},
        executed=True,
        status="success",
        external_calls=1,
        service_version=settings.service_version,
        runtime=_runtime(settings, args.provider),
        result=result_payload,
        root=ROOT,
        release_manifest=args.release_manifest,
        started_at=started_at,
        finished_at=utc_now(),
    )
    bundle = write_live_validation_bundle(evidence, args.evidence_dir)
    print(json.dumps({"status": "success", "provider": args.provider, "bundle": bundle}, sort_keys=True))


if __name__ == "__main__":
    main()
