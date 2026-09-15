from __future__ import annotations

import argparse
import json
from pathlib import Path

from release_evidence import ROOT, service_version


def release_version_errors(root: Path = ROOT, tag: str | None = None) -> list[str]:
    root = root.resolve()
    version = service_version(root)
    expected_tag = f"v{version}"
    errors: list[str] = []

    expected_fragments = {
        ".env.example": [f"ARO_SERVICE_VERSION={version}"],
        "docker-compose.yml": [
            f"image: autonomous-revenue-ops:{version}",
            f"ARO_SERVICE_VERSION: {version}",
        ],
        "deploy/k8s/configmap.yaml": [f'ARO_SERVICE_VERSION: "{version}"'],
        "deploy/k8s/deployment.yaml": [f"image: ghcr.io/h00w/autonomous-revenue-ops:{version}"],
    }

    for relative, fragments in expected_fragments.items():
        path = root / relative
        if not path.is_file():
            errors.append(f"missing_versioned_file:{relative}")
            continue
        content = path.read_text(encoding="utf-8")
        for fragment in fragments:
            if fragment not in content:
                errors.append(f"version_mismatch:{relative}:{fragment}")

    if tag is not None and tag != expected_tag:
        errors.append(f"tag_version_mismatch:expected={expected_tag}:actual={tag}")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag")
    args = parser.parse_args()

    version = service_version(ROOT)
    errors = release_version_errors(ROOT, args.tag)
    report = {
        "evidence_class": "release_version_contract",
        "service_version": version,
        "expected_tag": f"v{version}",
        "supplied_tag": args.tag,
        "passed": not errors,
        "errors": errors,
        "network_calls": 0,
    }
    print(json.dumps(report, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
