import json
from pathlib import Path

import pytest

from src.evidence.live_validation import (
    build_live_validation_evidence,
    fingerprint_identifier,
    runtime_fingerprint,
    sanitize_url,
    validate_release_binding,
    verify_live_validation_bundle,
    write_live_validation_bundle,
)


SOURCE_SHA = "a" * 40
VERSION = "0.10.0"


def _release_manifest(tmp_path: Path) -> Path:
    path = tmp_path / "manifest.json"
    path.write_text(
        json.dumps(
            {
                "evidence_class": "release_integrity_manifest",
                "source_commit": SOURCE_SHA,
                "service_version": VERSION,
            }
        ),
        encoding="utf-8",
    )
    return path


def _runtime() -> dict:
    return runtime_fingerprint(
        environment="test",
        service_version=VERSION,
        subject_kind="model",
        subject_name="openai",
        model="example-model",
        target_url="https://user:password@example.com/v1?token=secret#fragment",
        credential_configured=True,
    )


def test_sanitize_url_removes_credentials_query_and_fragment():
    assert sanitize_url("https://user:pass@example.com:8443/path?q=1#x") == "https://example.com:8443/path"


def test_sanitize_url_does_not_raise_on_invalid_port_text():
    assert sanitize_url("https://user:pass@example.com:not-a-port/path?token=x") == "https://example.com/path"


def test_identifier_fingerprint_is_stable_and_non_reversible_shape():
    value = fingerprint_identifier("crm-record-123")
    assert value == fingerprint_identifier("crm-record-123")
    assert value != "crm-record-123"
    assert len(value or "") == 64


def test_release_preflight_succeeds_only_for_exact_commit_and_version(tmp_path: Path):
    manifest = _release_manifest(tmp_path)
    binding = validate_release_binding(
        service_version=VERSION,
        root=tmp_path,
        release_manifest=manifest,
        source_commit=SOURCE_SHA,
    )
    assert binding["present"] is True
    assert binding["source_commit"] == SOURCE_SHA
    assert binding["service_version"] == VERSION
    assert len(binding["sha256"]) == 64


def test_release_preflight_blocks_mismatch_before_live_execution(tmp_path: Path):
    manifest = _release_manifest(tmp_path)
    with pytest.raises(ValueError, match="source_commit mismatch"):
        validate_release_binding(
            service_version=VERSION,
            root=tmp_path,
            release_manifest=manifest,
            source_commit="b" * 40,
        )


def test_executed_live_evidence_requires_release_manifest(tmp_path: Path):
    with pytest.raises(ValueError, match="requires a release integrity manifest"):
        build_live_validation_evidence(
            evidence_class="live_provider_smoke",
            subject={"kind": "model", "name": "openai"},
            executed=True,
            status="success",
            external_calls=1,
            service_version=VERSION,
            runtime=_runtime(),
            result={"ok": True},
            source_commit=SOURCE_SHA,
            root=tmp_path,
            prompt_manifest_path=None,
        )


def test_release_manifest_must_match_source_commit(tmp_path: Path):
    manifest = _release_manifest(tmp_path)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["source_commit"] = "b" * 40
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="source_commit mismatch"):
        build_live_validation_evidence(
            evidence_class="live_provider_smoke",
            subject={"kind": "model", "name": "openai"},
            executed=True,
            status="success",
            external_calls=1,
            service_version=VERSION,
            runtime=_runtime(),
            result={"ok": True},
            source_commit=SOURCE_SHA,
            root=tmp_path,
            release_manifest=manifest,
            prompt_manifest_path=None,
        )


def test_dry_run_cannot_claim_external_calls(tmp_path: Path):
    with pytest.raises(ValueError, match="zero external calls"):
        build_live_validation_evidence(
            evidence_class="validation_harness_contract",
            subject={"kind": "contract", "name": "test"},
            executed=False,
            status="dry-run",
            external_calls=1,
            service_version=VERSION,
            runtime=_runtime(),
            result={"ok": True},
            source_commit=SOURCE_SHA,
            root=tmp_path,
            prompt_manifest_path=None,
        )


def test_secret_bearing_result_key_is_rejected(tmp_path: Path):
    with pytest.raises(ValueError, match="forbidden secret-bearing key"):
        build_live_validation_evidence(
            evidence_class="validation_harness_contract",
            subject={"kind": "contract", "name": "test"},
            executed=False,
            status="dry-run",
            external_calls=0,
            service_version=VERSION,
            runtime=_runtime(),
            result={"api_key": "must-not-be-retained"},
            source_commit=SOURCE_SHA,
            root=tmp_path,
            prompt_manifest_path=None,
        )


def test_bundle_verifier_detects_tampering(tmp_path: Path):
    evidence = build_live_validation_evidence(
        evidence_class="validation_harness_contract",
        subject={"kind": "contract", "name": "test"},
        executed=False,
        status="dry-run",
        external_calls=0,
        service_version=VERSION,
        runtime=_runtime(),
        result={"ok": True},
        source_commit=SOURCE_SHA,
        root=tmp_path,
        prompt_manifest_path=None,
    )
    bundle_dir = tmp_path / "bundle"
    write_live_validation_bundle(evidence, bundle_dir)
    assert verify_live_validation_bundle(bundle_dir, root=tmp_path) == []

    evidence_path = bundle_dir / "evidence.json"
    evidence_path.write_text(evidence_path.read_text(encoding="utf-8") + " ", encoding="utf-8")
    assert "checksum_mismatch:evidence.json" in verify_live_validation_bundle(bundle_dir, root=tmp_path)


def test_valid_live_bundle_binds_release_manifest(tmp_path: Path):
    manifest = _release_manifest(tmp_path)
    evidence = build_live_validation_evidence(
        evidence_class="live_integration_smoke",
        subject={"kind": "integration", "name": "hubspot"},
        executed=True,
        status="success",
        external_calls=1,
        service_version=VERSION,
        runtime=runtime_fingerprint(
            environment="test",
            service_version=VERSION,
            subject_kind="integration",
            subject_name="hubspot",
            target_url="https://api.example.com",
            credential_configured=True,
        ),
        result={"record_id_sha256": fingerprint_identifier("record-1")},
        source_commit=SOURCE_SHA,
        root=tmp_path,
        release_manifest=manifest,
        prompt_manifest_path=None,
    )
    output = tmp_path / "live"
    write_live_validation_bundle(evidence, output)
    assert verify_live_validation_bundle(output, root=tmp_path) == []
