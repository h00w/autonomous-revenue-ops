import json
from pathlib import Path

from scripts.release_evidence import ROOT, base_image, build_release_evidence, parse_runtime_lock
from scripts.verify_release_evidence import verify_release_evidence


def test_runtime_lock_is_exact_and_nonempty():
    packages = parse_runtime_lock(ROOT)
    assert len(packages) >= 20
    raw = (ROOT / "requirements-api.lock").read_text(encoding="utf-8")
    assert ">=" not in raw
    assert "~=" not in raw
    assert all(name and version for name, version in packages)


def test_base_image_is_digest_pinned():
    image = base_image(ROOT)
    assert image["reference"] == "python:3.12-slim-bookworm"
    assert image["digest"].startswith("sha256:")
    assert len(image["digest"]) == 71


def test_release_evidence_generates_spdx_manifest_and_honest_provenance(tmp_path):
    commit = "a" * 40
    result = build_release_evidence(ROOT, tmp_path, source_commit=commit)
    assert result["evidence_class"] == "release_integrity_bundle"
    assert result["signed"] is False

    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    sbom = json.loads((tmp_path / "sbom.spdx.json").read_text(encoding="utf-8"))
    provenance = json.loads((tmp_path / "provenance.json").read_text(encoding="utf-8"))

    assert manifest["source_commit"] == commit
    assert manifest["evidence_class"] == "release_integrity_manifest"
    assert ".env" not in manifest["files"]
    assert sbom["spdxVersion"] == "SPDX-2.3"
    assert len(sbom["packages"]) == len(parse_runtime_lock(ROOT))
    assert provenance["source_commit"] == commit
    assert provenance["attestation"]["signed"] is False
    assert provenance["attestation"]["slsa_statement"] is False
    assert verify_release_evidence(ROOT, tmp_path) == []


def test_verifier_detects_tampered_generated_evidence(tmp_path):
    build_release_evidence(ROOT, tmp_path, source_commit="b" * 40)
    (tmp_path / "sbom.spdx.json").write_text("{}\n", encoding="utf-8")
    errors = verify_release_evidence(ROOT, tmp_path)
    assert "checksum_mismatch:sbom.spdx.json" in errors
