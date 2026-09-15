from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pydantic import BaseModel

from src.ai.factory import build_ai_router
from src.ai.models import StructuredGenerationRequest
from src.ai.router import ModelRouter
from src.ai.schema import strict_model_schema
from src.config import Settings
from src.evidence.live_validation import (
    build_live_validation_evidence,
    runtime_fingerprint,
    utc_now,
    write_live_validation_bundle,
)


class SmokeOutput(BaseModel):
    status: str
    note: str


def _runtime(settings: Settings, provider: str) -> dict:
    return runtime_fingerprint(
        environment=settings.environment,
        service_version=settings.service_version,
        subject_kind="model",
        subject_name=provider,
        model=getattr(settings, f"{provider}_model"),
        target_url=getattr(settings, f"{provider}_base_url"),
        credential_configured=getattr(settings, f"{provider}_api_key") is not None,
        extra={"ai_timeout_seconds": settings.ai_timeout_seconds},
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="AI provider capability smoke check")
    parser.add_argument("provider", choices=["openai", "anthropic", "gemini"])
    parser.add_argument("--execute", action="store_true", help="Make one real provider API call")
    parser.add_argument("--evidence-dir", type=Path, help="Required with --execute.")
    parser.add_argument("--release-manifest", type=Path, default=Path("release-evidence/manifest.json"))
    args = parser.parse_args()

    if not args.execute:
        print(
            json.dumps(
                {
                    "status": "dry-run",
                    "provider": args.provider,
                    "external_calls": 0,
                    "message": "No external call made. Re-run with --execute and --evidence-dir after configuring a dedicated API key.",
                }
            )
        )
        return

    if args.evidence_dir is None:
        raise SystemExit("--evidence-dir is required with --execute so live capability evidence is retained")

    settings = Settings(ai_provider_order=args.provider)
    router: ModelRouter = build_ai_router(settings)
    started_at = utc_now()
    try:
        request = StructuredGenerationRequest(
            system_prompt="Return a minimal structured health response. Do not perform any external action.",
            user_prompt="Return status=ok and a short note.",
            schema_name="SmokeOutput",
            json_schema=strict_model_schema(SmokeOutput),
            prompt_id="smoke.ai_provider",
            prompt_version="1.0.0",
            max_output_tokens=128,
        )
        output, result = router.generate_typed(request, SmokeOutput)
    finally:
        router.close()

    result_payload = {
        "provider": result.provider,
        "model": result.model,
        "output": output.model_dump(),
        "request_id_sha256": None,
        "input_tokens": result.input_tokens,
        "output_tokens": result.output_tokens,
        "latency_ms": result.latency_ms,
        "routing_attempts": [attempt.model_dump(mode="json") for attempt in result.routing_attempts],
    }
    if result.request_id:
        from src.evidence.live_validation import fingerprint_identifier

        result_payload["request_id_sha256"] = fingerprint_identifier(result.request_id)

    evidence = build_live_validation_evidence(
        evidence_class="live_provider_smoke",
        subject={
            "kind": "model",
            "name": args.provider,
            "configured_model": getattr(settings, f"{args.provider}_model"),
        },
        executed=True,
        status="success",
        external_calls=max(1, len(result.routing_attempts)),
        service_version=settings.service_version,
        runtime=_runtime(settings, args.provider),
        result=result_payload,
        root=ROOT,
        release_manifest=args.release_manifest,
        started_at=started_at,
        finished_at=utc_now(),
    )
    bundle = write_live_validation_bundle(evidence, args.evidence_dir)
    print(
        json.dumps(
            {
                "status": "success",
                "provider": result.provider,
                "model": result.model,
                "bundle": bundle,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
