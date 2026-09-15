import os
from pathlib import Path

from ..config import Settings


def deployment_readiness_checks(settings: Settings) -> dict[str, str]:
    """Return deployment checks without contacting external providers.

    Production readiness is intentionally fail-closed for secrets required at the
    HTTP/workflow boundary and for at least one configured model provider.
    SQLite is accepted only for a single application replica.
    """

    checks: dict[str, str] = {}
    if settings.environment != "production":
        return checks

    checks["workflow_api_auth"] = "ok" if settings.workflow_api_key else "missing"
    checks["webhook_signing"] = "ok" if settings.webhook_signing_secret else "missing"
    checks["ai_provider_configuration"] = (
        "ok"
        if any((settings.openai_api_key, settings.anthropic_api_key, settings.gemini_api_key))
        else "missing"
    )

    if settings.workflow_store_backend == "sqlite":
        checks["sqlite_single_replica"] = (
            "ok" if settings.deployment_replica_count == 1 else "invalid"
        )
        parent = Path(settings.workflow_db_path).expanduser().resolve().parent
        checks["workflow_storage"] = (
            "ok" if parent.exists() and os.access(parent, os.W_OK) else "unwritable"
        )
    else:
        checks["workflow_storage"] = "ok"

    return checks
