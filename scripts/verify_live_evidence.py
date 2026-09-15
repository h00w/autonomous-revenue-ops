from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.evidence.live_validation import verify_live_validation_bundle  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify a retained live-validation evidence bundle")
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--skip-materials", action="store_true")
    args = parser.parse_args()

    errors = verify_live_validation_bundle(
        args.bundle,
        root=ROOT,
        verify_materials=not args.skip_materials,
    )
    report = {
        "evidence_class": "live_validation_verification",
        "passed": not errors,
        "errors": errors,
        "network_calls": 0,
    }
    print(json.dumps(report, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
