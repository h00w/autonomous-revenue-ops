from pathlib import Path

from fastapi.testclient import TestClient

import src.api as api_module
from src.config import Settings
from src.operations.readiness import deployment_readiness_checks
from src.service import RevenueOpsService


def production_settings(tmp_path: Path, **updates) -> Settings:
    values = {
        "environment": "production",
        "service_version": "0.8.0",
        "workflow_store_backend": "sqlite",
        "workflow_db_path": str(tmp_path / "workflows.sqlite3"),
        "deployment_replica_count": 1,
        "workflow_api_key": "workflow-secret",
        "webhook_signing_secret": "webhook-secret",
        "openai_api_key": "provider-key",
    }
    values.update(updates)
    return Settings(_env_file=None, **values)


def test_production_readiness_accepts_single_replica_writable_sqlite(tmp_path):
    checks = deployment_readiness_checks(production_settings(tmp_path))
    assert checks == {
        "workflow_api_auth": "ok",
        "webhook_signing": "ok",
        "ai_provider_configuration": "ok",
        "sqlite_single_replica": "ok",
        "workflow_storage": "ok",
    }


def test_sqlite_multi_replica_configuration_fails_closed(tmp_path):
    checks = deployment_readiness_checks(production_settings(tmp_path, deployment_replica_count=2))
    assert checks["sqlite_single_replica"] == "invalid"


def test_missing_production_security_and_ai_configuration_is_not_ready(tmp_path):
    checks = deployment_readiness_checks(
        production_settings(
            tmp_path,
            workflow_api_key=None,
            webhook_signing_secret=None,
            openai_api_key=None,
        )
    )
    assert checks["workflow_api_auth"] == "missing"
    assert checks["webhook_signing"] == "missing"
    assert checks["ai_provider_configuration"] == "missing"


def test_production_readiness_endpoint_returns_503_when_required_config_missing(tmp_path, monkeypatch):
    settings = production_settings(
        tmp_path,
        workflow_api_key=None,
        webhook_signing_secret=None,
        openai_api_key=None,
    )
    monkeypatch.setattr(api_module, "settings", settings)
    monkeypatch.setattr(api_module, "service", RevenueOpsService(settings=settings))
    client = TestClient(api_module.create_app())

    response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json()["status"] == "degraded"
