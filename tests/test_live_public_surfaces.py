import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def test_render_n8n_blueprint_is_pinned_and_postgres_backed():
    blueprint = yaml.safe_load((ROOT / "render.yaml").read_text(encoding="utf-8"))
    service = blueprint["services"][0]

    assert service["type"] == "web"
    assert service["runtime"] == "image"
    assert service["region"] == "frankfurt"
    assert service["image"]["url"] == "docker.io/n8nio/n8n:2.38.7"
    assert service["healthCheckPath"] == "/healthz"

    env = {item["key"]: item for item in service["envVars"]}
    assert env["DB_TYPE"]["value"] == "postgresdb"
    assert env["N8N_ENCRYPTION_KEY"]["generateValue"] is True
    assert env["N8N_WEBHOOK_URL"]["value"].startswith("https://")
    assert "WEBHOOK_URL" not in env
    assert env["N8N_PROXY_HOPS"]["value"] == "1"
    assert env["NODE_OPTIONS"]["value"] == "--max-old-space-size=384"
    assert env["N8N_UNVERIFIED_PACKAGES_ENABLED"]["value"] == "false"
    assert env["N8N_RUNNERS_TASK_TIMEOUT"]["value"] == "60"
    assert env["N8N_COMPRESSION_NODE_MAX_DECOMPRESSED_SIZE_BYTES"]["value"] == "268435456"
    assert env["N8N_COMPRESSION_NODE_MAX_ZIP_ENTRIES"]["value"] == "1000"

    database_refs = {
        env[key]["fromDatabase"]["name"]
        for key in (
            "DB_POSTGRESDB_DATABASE",
            "DB_POSTGRESDB_HOST",
            "DB_POSTGRESDB_PASSWORD",
            "DB_POSTGRESDB_USER",
        )
    }
    assert database_refs == {"autonomous-revenue-ops-n8n-db"}
    assert blueprint["databases"][0]["name"] == "autonomous-revenue-ops-n8n-db"


def test_render_blueprint_contains_no_staging_credentials():
    text = (ROOT / "render.yaml").read_text(encoding="utf-8")

    assert "X-ARO-API-Key" not in text
    assert "ARO_WORKFLOW_API_KEY" not in text
    assert "ARO_WEBHOOK_SIGNING_SECRET" not in text
    assert "password:" not in text.lower()


def test_public_demo_doc_records_live_staging_surfaces():
    text = (ROOT / "docs" / "public-demo-stack.md").read_text(encoding="utf-8")

    assert "https://autonomous-revenue-ops-staging.onrender.com" in text
    assert "https://autonomous-revenue-ops-dashboard.onrender.com" in text
    assert "not Production Validated" in text or "not production validation" in text.lower()
    assert "ephemeral" in text.lower()


def test_postman_collection_targets_live_staging_without_credentials():
    collection = json.loads(
        (ROOT / "postman" / "autonomous-revenue-ops.postman_collection.json").read_text(
            encoding="utf-8"
        )
    )
    variables = {item["key"]: item["value"] for item in collection["variable"]}

    assert variables["base_url"] == "https://autonomous-revenue-ops-staging.onrender.com"
    assert variables["aro_api_key"] == ""
