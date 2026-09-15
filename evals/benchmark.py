import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.models import LeadInput, Qualification  # noqa: E402
from src.policy import evaluate_policy  # noqa: E402


def run(path: str | Path | None = None):
    dataset_path = Path(path) if path is not None else ROOT / "data" / "lead_qualification_eval.jsonl"
    cases = [
        json.loads(line)
        for line in dataset_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    passed = 0
    rows = []
    for case in cases:
        lead = LeadInput(
            lead_id=case["case_id"],
            name="Synthetic Lead",
            email=f'{case["case_id"]}@example.com',
            company="Synthetic Company",
            consent_to_contact=case["lead"]["consent_to_contact"],
        )
        q = Qualification(
            score=case["qualification"]["score"],
            confidence=case["qualification"]["confidence"],
            icp_fit=80,
            intent=80,
            urgency=60,
            risk_flags=case["qualification"].get("risk_flags", []),
        )
        actual = evaluate_policy(lead, q).decision.value
        ok = actual == case["expected_decision"]
        passed += int(ok)
        rows.append((case["case_id"], case["expected_decision"], actual, ok))

    total = len(cases)
    accuracy = passed / total if total else 0.0
    print(f"Policy benchmark: {passed}/{total} passed ({accuracy:.1%})")
    for row in rows:
        print(f"{row[0]} expected={row[1]} actual={row[2]} pass={row[3]}")
    if accuracy < 1.0:
        raise SystemExit(1)


if __name__ == "__main__":
    run()
