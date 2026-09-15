from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.release_evidence import sha256_file  # noqa: E402


def verify_release_evidence(root: Path, evidence_dir: Path | str) -> list[str]:
    root = root.resolve()
    evidence = Path(evidence_dir)
    if not evidence.is_absolute():
        evidence = root / evidence

    errors: list[str] = []
    required = ["manifest.json", "sbom.spdx.json", "provenance.json", "SHA256SUMS"]
    for name in required:
        if not (evidence / name).is_file():
            errors.append(f"missing_evidence_file:{name}")
    if errors:
        return errors

    expected_sums: dict[str, str] = {}
    for line in (evidence / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            digest, name = line.split(None, 1)
        except ValueError:
            errors.append("invalid_sha256sums_line")
            continue
        expected_sums[name.strip()] = digest.strip()

    for name in ("manifest.json", "sbom.spdx.json", "provenance.json"):
        expected = expected_sums.get(name)
        if expected is None:
            errors.append(f"missing_checksum:{name}")
        elif sha256_file(evidence / name) != expected:
            errors.append(f"checksum_mismatch:{name}")

    manifest = json.loads((evidence / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("evidence_class") != "release_integrity_manifest":
        errors.append("invalid_manifest_evidence_class")
    for relative, expected in manifest.get("files", {}).items():
        path = root / relative
        if not path.is_file():
            errors.append(f"missing_source_file:{relative}")
        elif sha256_file(path) != expected:
            errors.append(f"source_checksum_mismatch:{relative}")

    sbom = json.loads((evidence / "sbom.spdx.json").read_text(encoding="utf-8"))
    if sbom.get("spdxVersion") != "SPDX-2.3":
        errors.append("invalid_spdx_version")
    if not sbom.get("packages"):
        errors.append("empty_sbom")

    provenance = json.loads((evidence / "provenance.json").read_text(encoding="utf-8"))
    if provenance.get("evidence_class") != "build_provenance_metadata":
        errors.append("invalid_provenance_evidence_class")
    if provenance.get("source_commit") != manifest.get("source_commit"):
        errors.append("source_commit_mismatch")
    attestation = provenance.get("attestation", {})
    if attestation.get("signed") is not False or attestation.get("slsa_statement") is not False:
        errors.append("unsigned_metadata_must_not_claim_signed_slsa_attestation")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence_dir", nargs="?", default="release-evidence")
    args = parser.parse_args()
    errors = verify_release_evidence(ROOT, args.evidence_dir)
    result = {
        "evidence_class": "release_integrity_verification",
        "passed": not errors,
        "errors": errors,
        "network_calls": 0,
    }
    print(json.dumps(result, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
