from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[2]
PROMPT_MANIFEST = ROOT / "evals" / "prompt_manifest.json"
DEFAULT_RELEASE_MANIFEST = ROOT / "release-evidence" / "manifest.json"

LIVE_CLASSES = {
    "live_provider_eval",
    "live_provider_smoke",
    "live_integration_smoke",
    "live_deployment_probe",
}
FORBIDDEN_KEYS = {
    "api_key",
    "access_token",
    "authorization",
    "password",
    "secret",
    "smtp_password",
    "token",
    "webhook_url",
    "workflow_api_key",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fingerprint_identifier(value: str | None) -> str | None:
    if value is None:
        return None
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def resolve_source_commit(root: Path = ROOT, explicit: str | None = None) -> str:
    value = explicit or os.getenv("ARO_SOURCE_COMMIT") or os.getenv("GITHUB_SHA")
    if value:
        return value
    return _git(root, "rev-parse", "HEAD")


def _validated_source_commit(root: Path, explicit: str | None = None) -> str:
    commit = resolve_source_commit(root, explicit)
    if not re.fullmatch(r"[0-9a-fA-F]{40}", commit):
        raise ValueError(f"source_commit must be a 40-character git SHA: {commit}")
    return commit


def sanitize_url(value: str | None) -> str | None:
    """Retain a useful target/origin while removing credentials, query and fragment."""
    if not value:
        return None
    parsed = urlsplit(value)
    if not parsed.scheme or not parsed.netloc:
        return value.split("?", 1)[0].split("#", 1)[0]
    host = parsed.hostname or ""
    try:
        port = parsed.port
    except ValueError:
        port = None
    if port:
        host = f"{host}:{port}"
    return urlunsplit((parsed.scheme, host, parsed.path or "", "", ""))


def runtime_fingerprint(
    *,
    environment: str,
    service_version: str,
    subject_kind: str,
    subject_name: str,
    model: str | None = None,
    target_url: str | None = None,
    credential_configured: bool | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    data: dict[str, Any] = {
        "environment": environment,
        "service_version": service_version,
        "subject_kind": subject_kind,
        "subject_name": subject_name,
        "python_version": platform.python_version(),
        "platform": platform.system().lower(),
    }
    if model is not None:
        data["model"] = model
    if target_url is not None:
        data["target"] = sanitize_url(target_url)
    if credential_configured is not None:
        data["credential_configured"] = bool(credential_configured)
    if extra:
        data["extra"] = extra
    _assert_secret_safe(data)
    return data


def _assert_secret_safe(value: Any, path: str = "root") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).strip().lower()
            if normalized in FORBIDDEN_KEYS:
                raise ValueError(f"forbidden secret-bearing key in evidence: {path}.{key}")
            _assert_secret_safe(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _assert_secret_safe(item, f"{path}[{index}]")


def _relative_or_absolute(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def _material(root: Path, path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.is_file():
        return None
    return {
        "path": _relative_or_absolute(root, path),
        "sha256": sha256_file(path),
    }


def _release_binding(
    root: Path,
    release_manifest: Path | None,
    *,
    source_commit: str,
    service_version: str,
    required: bool,
) -> dict[str, Any]:
    manifest_path = release_manifest or DEFAULT_RELEASE_MANIFEST
    if not manifest_path.is_absolute():
        manifest_path = root / manifest_path
    if not manifest_path.is_file():
        if required:
            raise ValueError(
                "executed live validation requires a release integrity manifest; "
                "generate release-evidence/manifest.json from the exact source commit first"
            )
        return {"present": False}

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_commit = payload.get("source_commit")
    manifest_version = payload.get("service_version")
    if manifest_commit != source_commit:
        raise ValueError(
            f"release manifest source_commit mismatch: expected {source_commit}, got {manifest_commit}"
        )
    if manifest_version != service_version:
        raise ValueError(
            f"release manifest service_version mismatch: expected {service_version}, got {manifest_version}"
        )
    return {
        "present": True,
        "path": _relative_or_absolute(root, manifest_path),
        "sha256": sha256_file(manifest_path),
        "source_commit": manifest_commit,
        "service_version": manifest_version,
        "evidence_class": payload.get("evidence_class"),
    }


def validate_release_binding(
    *,
    service_version: str,
    root: Path = ROOT,
    release_manifest: Path | None = None,
    source_commit: str | None = None,
) -> dict[str, Any]:
    """Fail before a live side effect unless release provenance matches this source/version."""
    root = root.resolve()
    commit = _validated_source_commit(root, source_commit)
    return _release_binding(
        root,
        release_manifest,
        source_commit=commit,
        service_version=service_version,
        required=True,
    )


def build_live_validation_evidence(
    *,
    evidence_class: str,
    subject: dict[str, Any],
    executed: bool,
    status: str,
    external_calls: int,
    service_version: str,
    runtime: dict[str, Any],
    result: dict[str, Any],
    root: Path = ROOT,
    source_commit: str | None = None,
    dataset_path: Path | None = None,
    prompt_manifest_path: Path | None = PROMPT_MANIFEST,
    release_manifest: Path | None = None,
    started_at: str | None = None,
    finished_at: str | None = None,
) -> dict[str, Any]:
    root = root.resolve()
    commit = _validated_source_commit(root, source_commit)
    if external_calls < 0:
        raise ValueError("external_calls cannot be negative")
    if executed and evidence_class in LIVE_CLASSES and external_calls < 1:
        raise ValueError("executed live evidence must record at least one external call")
    if not executed and external_calls != 0:
        raise ValueError("dry-run evidence must record zero external calls")

    release = _release_binding(
        root,
        release_manifest,
        source_commit=commit,
        service_version=service_version,
        required=executed and evidence_class in LIVE_CLASSES,
    )
    materials = {
        "prompt_manifest": _material(root, prompt_manifest_path),
        "dataset": _material(root, dataset_path),
    }
    started = started_at or utc_now()
    finished = finished_at or utc_now()

    payload = {
        "schema_version": "1.0",
        "validation_id": str(uuid.uuid4()),
        "evidence_class": evidence_class,
        "executed": executed,
        "status": status,
        "external_calls": external_calls,
        "source": {
            "repository": "h00w/autonomous-revenue-ops",
            "source_commit": commit,
            "service_version": service_version,
        },
        "subject": subject,
        "materials": materials,
        "release_binding": release,
        "runtime": runtime,
        "window": {
            "started_at": started,
            "finished_at": finished,
        },
        "result": result,
        "evidence_boundaries": {
            "production_validated": False,
            "customer_roi_evidence": False,
            "single_run_is_long_window_slo": False,
            "note": (
                "Retained execution evidence proves only the named provider/integration/deployment "
                "behavior for this exact source/configuration and observation window."
            ),
        },
    }
    _assert_secret_safe(payload)
    return payload


def write_live_validation_bundle(
    evidence: dict[str, Any],
    output_dir: Path | str,
) -> dict[str, Any]:
    _assert_secret_safe(evidence)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    evidence_path = output / "evidence.json"
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    evidence_sha = sha256_file(evidence_path)
    (output / "SHA256SUMS").write_text(f"{evidence_sha}  evidence.json\n", encoding="utf-8")
    return {
        "evidence_class": "live_validation_bundle",
        "validation_id": evidence.get("validation_id"),
        "output_dir": str(output),
        "evidence_sha256": evidence_sha,
        "files": ["evidence.json", "SHA256SUMS"],
    }


def verify_live_validation_bundle(
    bundle_dir: Path | str,
    *,
    root: Path = ROOT,
    verify_materials: bool = True,
) -> list[str]:
    bundle = Path(bundle_dir)
    errors: list[str] = []
    evidence_path = bundle / "evidence.json"
    sums_path = bundle / "SHA256SUMS"
    if not evidence_path.is_file():
        return ["missing:evidence.json"]
    if not sums_path.is_file():
        return ["missing:SHA256SUMS"]

    line = sums_path.read_text(encoding="utf-8").strip()
    parts = line.split()
    if len(parts) != 2 or parts[1] != "evidence.json":
        errors.append("invalid:SHA256SUMS")
    else:
        actual = sha256_file(evidence_path)
        if actual != parts[0]:
            errors.append("checksum_mismatch:evidence.json")

    try:
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return errors + ["invalid_json:evidence.json"]

    try:
        _assert_secret_safe(evidence)
    except ValueError as exc:
        errors.append(f"secret_safety:{exc}")

    executed = bool(evidence.get("executed"))
    evidence_class = evidence.get("evidence_class")
    external_calls = evidence.get("external_calls")
    if executed and evidence_class in LIVE_CLASSES:
        if not evidence.get("release_binding", {}).get("present"):
            errors.append("missing:release_binding")
        if not isinstance(external_calls, int) or external_calls < 1:
            errors.append("invalid:external_calls_for_live_execution")
    if not executed and external_calls != 0:
        errors.append("invalid:dry_run_external_calls")
    if evidence.get("evidence_boundaries", {}).get("production_validated") is not False:
        errors.append("invalid:production_validated_boundary")

    source = evidence.get("source", {})
    release = evidence.get("release_binding", {})
    if release.get("present"):
        if release.get("source_commit") != source.get("source_commit"):
            errors.append("mismatch:release_source_commit")
        if release.get("service_version") != source.get("service_version"):
            errors.append("mismatch:release_service_version")

    if verify_materials:
        for name, material in (evidence.get("materials") or {}).items():
            if not material:
                continue
            path_value = material.get("path")
            expected = material.get("sha256")
            if not path_value or not expected:
                errors.append(f"invalid_material:{name}")
                continue
            candidate = Path(path_value)
            if not candidate.is_absolute():
                candidate = root / candidate
            if not candidate.is_file():
                errors.append(f"missing_material:{name}:{path_value}")
                continue
            if sha256_file(candidate) != expected:
                errors.append(f"material_hash_mismatch:{name}:{path_value}")

    return errors
