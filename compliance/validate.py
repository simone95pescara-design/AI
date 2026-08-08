from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
REQUIRED = [
    REPO / "AGENTS.md",
    REPO / "governance" / "SPECIFICATION.md",
    REPO / "governance" / "authority.md",
    REPO / "governance" / "knowledge-policy.md",
    REPO / "governance" / "response-protocol.md",
    REPO / "governance" / "invariants.md",
]
SCHEMAS = {
    "DEC": REPO / "schemas" / "decision.schema.json",
    "REQ": REPO / "schemas" / "requirement.schema.json",
    "RISK": REPO / "schemas" / "risk.schema.json",
}
ID_PATTERN = re.compile(r"\b(?:DEC|REQ|RISK)-\d{3,}\b")


def fail(code: str, message: str, errors: list[str]) -> None:
    errors.append(f"{code}: {message}")


def check_required_files(errors: list[str]) -> None:
    for path in REQUIRED:
        if not path.exists():
            fail("CHECK-001", f"missing required file: {path.relative_to(REPO)}", errors)


def check_schemas(errors: list[str]) -> None:
    for path in list(SCHEMAS.values()) + [REPO / "schemas" / "state.schema.json"]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            fail("CHECK-002", f"invalid schema {path.relative_to(REPO)}: {exc}", errors)
            continue
        if data.get("type") != "object" or not data.get("required"):
            fail("CHECK-002", f"schema lacks object/required contract: {path.relative_to(REPO)}", errors)


def check_duplicate_ids(errors: list[str]) -> None:
    seen: dict[str, Path] = {}
    roots = [REPO / "decisions", REPO / "requirements", REPO / "risks"]
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".md", ".yaml", ".yml", ".json"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for item_id in set(ID_PATTERN.findall(text)):
                if item_id in seen and seen[item_id] != path:
                    fail("INV-006", f"duplicate ID {item_id}: {seen[item_id].relative_to(REPO)} and {path.relative_to(REPO)}", errors)
                else:
                    seen[item_id] = path


def check_obvious_secrets(errors: list[str]) -> None:
    secret_patterns = [
        re.compile(r"AKIA[0-9A-Z]{16}"),
        re.compile(r"ghp_[A-Za-z0-9]{20,}"),
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    ]
    excluded = {".git"}
    for path in REPO.rglob("*"):
        if not path.is_file() or any(part in excluded for part in path.parts):
            continue
        if path.suffix.lower() not in {".md", ".py", ".json", ".yaml", ".yml", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in secret_patterns:
            if pattern.search(text):
                fail("INV-008", f"possible secret in {path.relative_to(REPO)}", errors)


def main() -> int:
    errors: list[str] = []
    check_required_files(errors)
    check_schemas(errors)
    check_duplicate_ids(errors)
    check_obvious_secrets(errors)

    if errors:
        print("COMPLIANCE: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("COMPLIANCE: PASS")
    print("- CHECK-001 required governance files present")
    print("- CHECK-002 schemas structurally valid")
    print("- INV-006 no duplicate persistent IDs detected")
    print("- INV-008 no obvious secrets detected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
