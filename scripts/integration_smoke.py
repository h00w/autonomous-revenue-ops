"""Opt-in live integration smoke test.

This script never executes external side effects unless --execute is supplied.
It is intended for HubSpot/Salesforce sandbox or dedicated test accounts and
for Slack/SMTP test destinations, not production customer records.
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
from src.integrations.factory import (  # noqa: E402
    build_crm_adapter,
    build_slack_notifier,
    build_smtp_adapter,
)
from src.integrations.models import CRMLeadRecord, EmailMessage  # noqa: E402


def smoke_record() -> CRMLeadRecord:
    email = os.getenv("ARO_SMOKE_EMAIL", "aro-smoke@example.com")
    return CRMLeadRecord(
        external_key=os.getenv("ARO_SMOKE_EXTERNAL_KEY", "aro_phase2_smoke"),
        email=email,
        first_name=os.getenv("ARO_SMOKE_FIRST_NAME", "ARO"),
        last_name=os.getenv("ARO_SMOKE_LAST_NAME", "SmokeTest"),
        company=os.getenv("ARO_SMOKE_COMPANY", "Autonomous Revenue Ops Test"),
        title="Integration Smoke Test",
        source="Other",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("provider", choices=["hubspot", "salesforce", "slack", "smtp"])
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually call the configured external sandbox/test service.",
    )
    args = parser.parse_args()
    settings = Settings()

    if not args.execute:
        print(
            json.dumps(
                {
                    "status": "dry-run",
                    "provider": args.provider,
                    "message": "No external call made. Re-run with --execute after configuring sandbox/test credentials.",
                }
            )
        )
        return

    if args.provider in {"hubspot", "salesforce"}:
        adapter = build_crm_adapter(settings, args.provider)
        try:
            result = adapter.upsert_lead(smoke_record())
        finally:
            adapter.close()
        print(
            json.dumps(
                {
                    "status": "success",
                    "provider": result.provider,
                    "record_id": result.record_id,
                    "created": result.created,
                    "updated": result.updated,
                }
            )
        )
        return

    if args.provider == "slack":
        notifier = build_slack_notifier(settings)
        try:
            result = notifier.send("Autonomous Revenue Ops Phase 2 integration smoke test")
        finally:
            notifier.close()
        print(json.dumps({"status": "success", "provider": result.provider, "delivered": result.delivered}))
        return

    adapter = build_smtp_adapter(settings)
    result = adapter.send(
        EmailMessage(
            to=os.getenv("ARO_SMOKE_EMAIL", "aro-smoke@example.com"),
            subject="Autonomous Revenue Ops Phase 2 smoke test",
            text="This is an explicit integration smoke test from the Phase 2 validation harness.",
        )
    )
    print(json.dumps({"status": "success", "provider": result.provider, "delivered": result.delivered}))


if __name__ == "__main__":
    main()
