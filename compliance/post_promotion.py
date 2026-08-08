from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]


def check_post_promotion(repo: Path = REPO) -> list[str]:
    errors: list[str] = []
    state_path = repo / "state" / "current.yaml"
    if not state_path.exists():
        return ["POST-001: missing state/current.yaml"]

    state = yaml.safe_load(state_path.read_text(encoding="utf-8")) or {}
    baseline = str(state.get("baseline", ""))

    dec2 = repo / "decisions" / "DEC-002.yaml"
    transition = repo / "governance" / "transition-model.md"
    if dec2.exists() and transition.exists():
        decision = yaml.safe_load(dec2.read_text(encoding="utf-8")) or {}
        header = "\n".join(transition.read_text(encoding="utf-8").splitlines()[:5])
        if decision.get("status") == "APPROVED":
            if "DEC-002" not in baseline:
                errors.append("POST-002: DEC-002 is APPROVED but state baseline does not include DEC-002")
            if "APPROVED_CANDIDATE" in header:
                errors.append("POST-003: promoted Transition Model still self-labels APPROVED_CANDIDATE")

    dec3 = repo / "decisions" / "DEC-003.yaml"
    operational = repo / "governance" / "operational-metamodel.md"
    if dec3.exists() and operational.exists():
        decision = yaml.safe_load(dec3.read_text(encoding="utf-8")) or {}
        header = "\n".join(operational.read_text(encoding="utf-8").splitlines()[:5])
        if decision.get("status") == "APPROVED" and "PROPOSED" in header:
            errors.append("POST-004: DEC-003 is APPROVED but Operational Metamodel still self-labels PROPOSED")

    return errors


def main() -> int:
    errors = check_post_promotion()
    if errors:
        print("POST-PROMOTION: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("POST-PROMOTION: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
