from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]

TRACKED_INPUTS = (
    "Dockerfile",
    "requirements-api.txt",
    "requirements-api.lock",
    "src",
    "evals/prompt_manifest.json",
    "evals/release_thresholds.json",
    "evals/live_agent_eval.py",
    "data/agent_eval_cases.jsonl",
    "deploy/k8s",
    "scripts/ai_provider_smoke.py",
    "scripts/integration_smoke.py",
    "scripts/slo_probe.py",
    "scripts/live_evidence_contract.py",
    "scripts/verify_live_evidence.py",
    "scripts/release_evidence.py",
    "scripts/verify_release_evidence.py",
    "scripts/release_version_check.py",
    "Makefile",
    ".github/workflows/ci.yml",
    ".github/workflows/release.yml",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def resolve_source_commit(root: Path, explicit: str | None = None) -> str:
    value = explicit or os.getenv("ARO_SOURCE_COMMIT") or os.getenv("GITHUB_SHA")
    if value:
        return value
    return _git(root, "rev-parse", "HEAD")


def service_version(root: Path) -> str:
    text = (root / "src/config.py").read_text(encoding="utf-8")
    match = re.search(r'service_version:\s*str\s*=\s*"([^"]+)"', text)
    if not match:
        raise ValueError("Could not resolve service_version from src/config.py")
    return match.group(1)


def base_image(root: Path) -> dict[str, str]:
    text = (root / "Dockerfile").read_text(encoding="utf-8")
    match = re.search(r"FROM\s+(python:[^\s@]+)@(sha256:[0-9a-f]{64})", text)
    if not match:
        raise ValueError("Dockerfile base image is not pinned by sha256 digest")
    return {"reference": match.group(1), "digest": match.group(2)}


def iter_input_files(root: Path) -> Iterable[Path]:
    seen: set[Path] = set()
    for item in TRACKED_INPUTS:
        path = root / item
        if path.is_file():
            resolved = path.resolve()
            if resolved not in seen:
                seen.add(resolved)
                yield path
            continue
        if not path.is_dir():
            raise FileNotFoundError(item)
        for child in sorted(path.rglob("*")):
            if not child.is_file():
                continue
            if "__pycache__" in child.parts or child.suffix in {".pyc", ".pyo"}:
                continue
            resolved = child.resolve()
            if resolved not in seen:
                seen.add(resolved)
                yield child


def source_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): sha256_file(path)
        for path in sorted(iter_input_files(root), key=lambda value: value.as_posix())
    }


def parse_runtime_lock(root: Path) -> list[tuple[str, str]]:
    packages: list[tuple[str, str]] = []
    for raw in (root / "requirements-api.lock").read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "==" not in line or any(token in line for token in (">=", "<=", "~=", "!=", "<", ">")):
            raise ValueError(f"Runtime lock entry is not exact: {line}")
        name, version = line.split("==", 1)
        if not name.strip() or not version.strip():
            raise ValueError(f"Invalid runtime lock entry: {line}")
        packages.append((name.strip(), version.strip()))
    return sorted(packages, key=lambda item: item[0].lower())


def _spdx_id(name: str, index: int) -> str:
    safe = re.sub(r"[^A-Za-z0-9.-]", "-", name)
    return f"SPDXRef-Package-{index}-{safe}"


def build_spdx(root: Path, source_commit: str, generated_at: str) -> dict:
    packages = []
    relationships = []
    for index, (name, version) in enumerate(parse_runtime_lock(root), start=1):
        spdx_id = _spdx_id(name, index)
        packages.append(
            {
                "name": name,
                "SPDXID": spdx_id,
                "versionInfo": version,
                "downloadLocation": "NOASSERTION",
                "filesAnalyzed": False,
                "licenseConcluded": "NOASSERTION",
                "licenseDeclared": "NOASSERTION",
                "copyrightText": "NOASSERTION",
                "externalRefs": [
                    {
                        "referenceCategory": "PACKAGE-MANAGER",
                        "referenceType": "purl",
                        "referenceLocator": f"pkg:pypi/{name.lower().replace('_', '-')}@{version}",
                    }
                ],
            }
        )
        relationships.append(
            {
                "spdxElementId": "SPDXRef-DOCUMENT",
                "relationshipType": "DESCRIBES",
                "relatedSpdxElement": spdx_id,
            }
        )
    return {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": "autonomous-revenue-ops-runtime-sbom",
        "documentNamespace": f"https://github.com/h00w/autonomous-revenue-ops/sbom/{source_commit}",
        "creationInfo": {
            "created": generated_at,
            "creators": ["Tool: autonomous-revenue-ops/scripts/release_evidence.py"],
        },
        "packages": packages,
        "relationships": relationships,
    }


def build_release_evidence(
    root: Path = ROOT,
    output_dir: Path | str = "release-evidence",
    *,
    source_commit: str | None = None,
    image_digest: str | None = None,
) -> dict:
    root = root.resolve()
    output = Path(output_dir)
    if not output.is_absolute():
        output = root / output
    output.mkdir(parents=True, exist_ok=True)

    commit = resolve_source_commit(root, source_commit)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    inputs = source_hashes(root)
    base = base_image(root)

    manifest = {
        "schema_version": "1.0",
        "evidence_class": "release_integrity_manifest",
        "project": "autonomous-revenue-ops",
        "service_version": service_version(root),
        "source_commit": commit,
        "runtime_dependency_lock_sha256": inputs["requirements-api.lock"],
        "base_image": base,
        "files": inputs,
        "evidence_boundaries": {
            "cryptographically_signed": False,
            "slsa_attestation": False,
            "live_provider_validation": False,
            "live_deployment_slo": False,
        },
    }
    manifest_path = output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    sbom_path = output / "sbom.spdx.json"
    sbom_path.write_text(
        json.dumps(build_spdx(root, commit, generated_at), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    provenance = {
        "schema_version": "1.0",
        "evidence_class": "build_provenance_metadata",
        "project": "autonomous-revenue-ops",
        "service_version": manifest["service_version"],
        "source_commit": commit,
        "generated_at": generated_at,
        "builder": {
            "system": "github-actions" if os.getenv("GITHUB_ACTIONS") == "true" else "local",
            "workflow": os.getenv("GITHUB_WORKFLOW"),
            "run_id": os.getenv("GITHUB_RUN_ID"),
        },
        "materials": {
            "integrity_manifest_sha256": sha256_file(manifest_path),
            "runtime_dependency_lock_sha256": inputs["requirements-api.lock"],
            "base_image": base,
        },
        "subject": {
            "container_image_digest": image_digest,
        },
        "attestation": {
            "signed": False,
            "slsa_statement": False,
            "note": "Project-generated provenance metadata; not a cryptographically signed SLSA attestation.",
        },
    }
    provenance_path = output / "provenance.json"
    provenance_path.write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    evidence_files = [manifest_path, sbom_path, provenance_path]
    sums = "".join(f"{sha256_file(path)}  {path.name}\n" for path in evidence_files)
    (output / "SHA256SUMS").write_text(sums, encoding="utf-8")

    return {
        "evidence_class": "release_integrity_bundle",
        "source_commit": commit,
        "service_version": manifest["service_version"],
        "output_dir": str(output),
        "files": [path.name for path in evidence_files] + ["SHA256SUMS"],
        "signed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="release-evidence")
    parser.add_argument("--source-commit")
    parser.add_argument("--image-digest")
    args = parser.parse_args()
    result = build_release_evidence(
        ROOT,
        args.output,
        source_commit=args.source_commit,
        image_digest=args.image_digest,
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
