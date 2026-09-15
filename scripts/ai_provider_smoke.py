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
from src.config import get_settings


class SmokeOutput(BaseModel):
    status: str
    note: str


def main() -> None:
    parser = argparse.ArgumentParser(description="AI provider capability smoke check")
    parser.add_argument("provider", choices=["openai", "anthropic", "gemini"])
    parser.add_argument("--execute", action="store_true", help="Make one real provider API call")
    args = parser.parse_args()

    if not args.execute:
        print(json.dumps({
            "status": "dry-run",
            "provider": args.provider,
            "message": "No external call made. Re-run with --execute after configuring a dedicated API key.",
        }))
        return

    settings = get_settings()
    settings.ai_provider_order = args.provider
    router: ModelRouter = build_ai_router(settings)
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
        print(json.dumps({
            "status": "success",
            "provider": result.provider,
            "model": result.model,
            "output": output.model_dump(),
            "attempts": [a.model_dump() for a in result.routing_attempts],
        }))
    finally:
        router.close()


if __name__ == "__main__":
    main()
