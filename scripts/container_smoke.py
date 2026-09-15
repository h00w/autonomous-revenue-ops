from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request


def _get(url: str, timeout: float) -> tuple[int, dict]:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:18000")
    parser.add_argument("--startup-timeout", type=float, default=30.0)
    args = parser.parse_args()

    deadline = time.monotonic() + args.startup_timeout
    live_status = None
    live_body = None
    while time.monotonic() < deadline:
        try:
            live_status, live_body = _get(args.base_url.rstrip("/") + "/health/live", 2.0)
            if live_status == 200:
                break
        except (urllib.error.URLError, TimeoutError, OSError):
            pass
        time.sleep(0.5)
    else:
        raise SystemExit("container failed to become live before timeout")

    ready_status, ready_body = _get(args.base_url.rstrip("/") + "/health/ready", 2.0)
    report = {
        "evidence_class": "container_runtime_smoke",
        "live_status": live_status,
        "ready_status": ready_status,
        "live_state": live_body.get("status") if live_body else None,
        "ready_state": ready_body.get("status"),
    }
    print(json.dumps(report, sort_keys=True))
    if live_status != 200 or ready_status != 200 or ready_body.get("status") != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
