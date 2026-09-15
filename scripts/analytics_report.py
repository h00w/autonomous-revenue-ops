"""Export a measured aggregate snapshot from the configured workflow store."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.analytics.service import AnalyticsService  # noqa: E402
from src.orchestration.runtime import get_workflow_store  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Export aggregate workflow analytics")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    snapshot = AnalyticsService(get_workflow_store()).snapshot()
    text = json.dumps(snapshot.model_dump(mode="json"), indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
