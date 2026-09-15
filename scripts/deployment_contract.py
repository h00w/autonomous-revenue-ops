from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []

    dockerfile = (root / "Dockerfile").read_text(encoding="utf-8")
    for required in (
        "FROM python:3.12-slim-bookworm",
        "USER 10001:10001",
        "HEALTHCHECK",
        "STOPSIGNAL SIGTERM",
    ):
        if required not in dockerfile:
            errors.append(f"dockerfile_missing:{required}")

    compose = _load_yaml(root / "docker-compose.yml")
    app = compose.get("services", {}).get("app", {})
    if app.get("read_only") is not True:
        errors.append("compose_root_filesystem_not_read_only")
    if "ALL" not in app.get("cap_drop", []):
        errors.append("compose_capabilities_not_dropped")
    if "no-new-privileges:true" not in app.get("security_opt", []):
        errors.append("compose_no_new_privileges_missing")
    if not any("/app/data" in str(item) for item in app.get("volumes", [])):
        errors.append("compose_persistent_data_mount_missing")
    if "healthcheck" not in app:
        errors.append("compose_healthcheck_missing")

    deployment = _load_yaml(root / "deploy/k8s/deployment.yaml")
    spec = deployment["spec"]
    pod_spec = spec["template"]["spec"]
    container = pod_spec["containers"][0]
    security = container.get("securityContext", {})
    pod_security = pod_spec.get("securityContext", {})

    if spec.get("replicas") != 1:
        errors.append("sqlite_reference_deployment_must_be_single_replica")
    if spec.get("strategy", {}).get("type") != "Recreate":
        errors.append("sqlite_reference_deployment_requires_recreate_strategy")
    if container.get("image", "").endswith(":latest"):
        errors.append("kubernetes_image_must_not_use_latest")
    if security.get("allowPrivilegeEscalation") is not False:
        errors.append("kubernetes_privilege_escalation_not_disabled")
    if security.get("readOnlyRootFilesystem") is not True:
        errors.append("kubernetes_root_filesystem_not_read_only")
    if "ALL" not in security.get("capabilities", {}).get("drop", []):
        errors.append("kubernetes_capabilities_not_dropped")
    if pod_security.get("runAsNonRoot") is not True or pod_security.get("runAsUser") != 10001:
        errors.append("kubernetes_non_root_identity_missing")
    if pod_security.get("seccompProfile", {}).get("type") != "RuntimeDefault":
        errors.append("kubernetes_seccomp_runtime_default_missing")
    if container.get("livenessProbe", {}).get("httpGet", {}).get("path") != "/health/live":
        errors.append("kubernetes_liveness_probe_invalid")
    if container.get("readinessProbe", {}).get("httpGet", {}).get("path") != "/health/ready":
        errors.append("kubernetes_readiness_probe_invalid")
    resources = container.get("resources", {})
    if not resources.get("requests") or not resources.get("limits"):
        errors.append("kubernetes_resource_bounds_missing")
    if not any(mount.get("mountPath") == "/app/data" for mount in container.get("volumeMounts", [])):
        errors.append("kubernetes_data_mount_missing")
    secret_refs = [item.get("secretRef", {}).get("name") for item in container.get("envFrom", [])]
    if "autonomous-revenue-ops-secrets" not in secret_refs:
        errors.append("kubernetes_secret_reference_missing")

    configmap = _load_yaml(root / "deploy/k8s/configmap.yaml")
    data = configmap.get("data", {})
    if data.get("ARO_ENVIRONMENT") != "production":
        errors.append("kubernetes_environment_not_production")
    if data.get("ARO_DEPLOYMENT_REPLICA_COUNT") != "1":
        errors.append("kubernetes_replica_runtime_contract_mismatch")

    pvc = _load_yaml(root / "deploy/k8s/pvc.yaml")
    if "ReadWriteOnce" not in pvc.get("spec", {}).get("accessModes", []):
        errors.append("sqlite_pvc_must_be_read_write_once")

    service = _load_yaml(root / "deploy/k8s/service.yaml")
    ports = service.get("spec", {}).get("ports", [])
    if not ports or ports[0].get("port") != 80 or ports[0].get("targetPort") != "http":
        errors.append("kubernetes_service_port_contract_invalid")

    # Secrets are referenced, never committed as Kubernetes Secret resources.
    for path in (root / "deploy/k8s").glob("*.yaml"):
        document = _load_yaml(path)
        if document.get("kind") == "Secret":
            errors.append(f"committed_kubernetes_secret_forbidden:{path.name}")

    return errors


def main() -> None:
    errors = validate()
    report = {
        "evidence_class": "static_deployment_contract",
        "passed": not errors,
        "errors": errors,
        "network_calls": 0,
        "sqlite_scaling_boundary": "single_replica",
    }
    print(json.dumps(report, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
