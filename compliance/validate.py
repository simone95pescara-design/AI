from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

REPO = Path(__file__).resolve().parents[1]
REQUIRED = [
    REPO / "AGENTS.md",
    REPO / "BOOTSTRAP.md",
    REPO / "governance" / "SPECIFICATION.md",
    REPO / "governance" / "authority.md",
    REPO / "governance" / "knowledge-policy.md",
    REPO / "governance" / "response-protocol.md",
    REPO / "governance" / "invariants.md",
    REPO / "governance" / "transition-model.md",
]
SCHEMAS = {
    "DEC": REPO / "schemas" / "decision.schema.json",
    "REQ": REPO / "schemas" / "requirement.schema.json",
    "RISK": REPO / "schemas" / "risk.schema.json",
    "STATE": REPO / "schemas" / "state.schema.json",
    "VER": REPO / "schemas" / "verification.schema.json",
    "QUEUE": REPO / "schemas" / "queue.schema.json",
    "DIA": REPO / "schemas" / "diagnostic.schema.json",
    "TASK": REPO / "schemas" / "task.schema.json",
}
ARTIFACT_ROOTS = {
    "DEC": REPO / "decisions",
    "REQ": REPO / "requirements",
    "RISK": REPO / "risks",
    "STATE": REPO / "state",
    "VER": REPO / "verification",
    "QUEUE": REPO / "queue",
    "DIA": REPO / "diagnostics",
    "TASK": REPO / "tasks",
}
ID_PATTERN = re.compile(r"\b(?:DEC|REQ|RISK|VER|QUEUE|DIA|TASK)-\d{3,}\b")
SUPPORTED_SUFFIXES = {".yaml", ".yml", ".json"}


def fail(code: str, message: str, errors: list[str]) -> None:
    errors.append(f"{code}: {message}")


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def check_required_files(errors: list[str]) -> None:
    for path in REQUIRED:
        if not path.exists():
            fail("CHECK-001", f"missing required file: {path.relative_to(REPO)}", errors)


def load_schema(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def check_schemas(errors: list[str]) -> None:
    for path in SCHEMAS.values():
        try:
            data = load_schema(path)
            Draft202012Validator.check_schema(data)
        except Exception as exc:
            fail("CHECK-002", f"invalid schema {path.relative_to(REPO)}: {exc}", errors)
            continue
        if data.get("type") != "object" or not data.get("required"):
            fail("CHECK-002", f"schema lacks object/required contract: {path.relative_to(REPO)}", errors)


def load_document(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    return yaml.safe_load(text)


def load_artifacts(errors: list[str]) -> list[tuple[str, Path, dict[str, Any]]]:
    artifacts: list[tuple[str, Path, dict[str, Any]]] = []
    for kind, root in ARTIFACT_ROOTS.items():
        if not root.exists():
            continue
        schema = load_schema(SCHEMAS[kind])
        validator = Draft202012Validator(schema)
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in SUPPORTED_SUFFIXES:
                continue
            try:
                data = load_document(path)
            except Exception as exc:
                fail("CHECK-003", f"cannot parse {path.relative_to(REPO)}: {exc}", errors)
                continue
            if not isinstance(data, dict):
                fail("CHECK-003", f"artifact must be an object: {path.relative_to(REPO)}", errors)
                continue
            schema_errors = sorted(validator.iter_errors(data), key=lambda item: list(item.absolute_path))
            for err in schema_errors:
                location = ".".join(str(part) for part in err.absolute_path) or "<root>"
                fail("CHECK-003", f"{path.relative_to(REPO)} [{location}]: {err.message}", errors)
            artifacts.append((kind, path, data))
    return artifacts


def check_duplicate_ids(artifacts: list[tuple[str, Path, dict[str, Any]]], errors: list[str]) -> None:
    seen: dict[str, Path] = {}
    for kind, path, data in artifacts:
        if kind == "STATE":
            continue
        item_id = data.get("id")
        if not isinstance(item_id, str):
            continue
        if item_id in seen and seen[item_id] != path:
            fail("INV-006", f"duplicate ID {item_id}: {seen[item_id].relative_to(REPO)} and {path.relative_to(REPO)}", errors)
        else:
            seen[item_id] = path


def extract_references(value: Any) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, str):
        refs.update(ID_PATTERN.findall(value))
    elif isinstance(value, list):
        for item in value:
            refs.update(extract_references(item))
    elif isinstance(value, dict):
        for item in value.values():
            refs.update(extract_references(item))
    return refs


def validate_semantics(artifacts: list[tuple[str, Path, dict[str, Any]]]) -> list[str]:
    errors: list[str] = []
    indexed: dict[str, tuple[str, Path, dict[str, Any]]] = {}
    for kind, path, data in artifacts:
        item_id = data.get("id")
        if kind != "STATE" and isinstance(item_id, str):
            indexed[item_id] = (kind, path, data)

    requirement_ids = {item_id for item_id, (kind, _, _) in indexed.items() if kind == "REQ"}

    for kind, path, data in artifacts:
        rel = path.relative_to(REPO) if path.is_absolute() else path
        item_id = data.get("id", str(rel))
        status = data.get("status")

        if kind == "DEC":
            if status == "APPROVED" and not nonempty(data.get("rationale")):
                fail("INV-002", f"approved decision {item_id} has no rationale ({rel})", errors)
            if status == "SUPERSEDED":
                successor = data.get("superseded_by")
                if not nonempty(successor):
                    fail("INV-003", f"superseded decision {item_id} must declare superseded_by ({rel})", errors)
                elif successor == item_id or successor not in indexed or indexed[successor][0] != "DEC":
                    fail("INV-003", f"superseded decision {item_id} points to invalid successor {successor!r} ({rel})", errors)
            for predecessor in data.get("supersedes", []) or []:
                if predecessor not in indexed or indexed[predecessor][0] != "DEC":
                    fail("INV-007", f"decision {item_id} supersedes missing decision {predecessor} ({rel})", errors)
                else:
                    old = indexed[predecessor][2]
                    if old.get("status") != "SUPERSEDED" or old.get("superseded_by") != item_id:
                        fail("INV-007", f"decision {item_id} supersedes {predecessor}, but reciprocal supersession is not recorded", errors)

        if kind == "REQ":
            if status == "APPROVED" and not nonempty(data.get("verification_method")):
                fail("INV-005", f"approved requirement {item_id} has no verification_method ({rel})", errors)
            if status == "SUPERSEDED":
                successor = data.get("superseded_by")
                if not nonempty(successor):
                    fail("INV-003", f"superseded requirement {item_id} must declare superseded_by ({rel})", errors)
                elif successor == item_id or successor not in indexed or indexed[successor][0] != "REQ":
                    fail("INV-003", f"superseded requirement {item_id} points to invalid successor {successor!r} ({rel})", errors)

        if kind == "VER":
            if status == "PASSED" and not (isinstance(data.get("evidence"), list) and data.get("evidence")):
                fail("INV-011", f"verification {item_id} is PASSED without evidence ({rel})", errors)

        if kind == "TASK":
            if status == "DONE" and data.get("verification_status") == "FAILED":
                fail("INV-004", f"task {item_id} is DONE with FAILED verification ({rel})", errors)
            if status == "DOING" and not nonempty(data.get("owner")):
                fail("INV-012", f"task {item_id} is DOING without explicit owner ({rel})", errors)

        if kind == "QUEUE" and status == "PROMOTED":
            target = data.get("promoted_to")
            if not nonempty(target) or target not in indexed or indexed[target][0] != "TASK":
                fail("INV-013", f"queue item {item_id} is PROMOTED without valid TASK target ({rel})", errors)

        if kind == "DIA":
            root_status = data.get("root_cause_status")
            root_cause = data.get("root_cause")
            if root_status == "CONFIRMED" and not nonempty(root_cause):
                fail("INV-014", f"diagnostic {item_id} confirms root cause without root_cause text ({rel})", errors)
            if root_status != "CONFIRMED" and status == "ROOT_CAUSE_CONFIRMED":
                fail("INV-014", f"diagnostic {item_id} status/root_cause_status conflict ({rel})", errors)

        if kind == "STATE":
            for key, expected_kind in (("active_tasks", "TASK"), ("queued_work", "QUEUE"), ("open_diagnostics", "DIA")):
                for ref in data.get(key, []) or []:
                    if ref not in indexed or indexed[ref][0] != expected_kind:
                        fail("INV-015", f"state projection {key} references missing {expected_kind} {ref} ({rel})", errors)

        for ref in extract_references(data):
            if ref.startswith("REQ-") and ref not in requirement_ids:
                fail("INV-001", f"{item_id} references missing requirement {ref} ({rel})", errors)

    return errors


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
    artifacts = load_artifacts(errors)
    check_duplicate_ids(artifacts, errors)
    errors.extend(validate_semantics(artifacts))
    check_obvious_secrets(errors)

    if errors:
        print("COMPLIANCE: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("COMPLIANCE: PASS")
    print("- CHECK-001 required governance files present")
    print("- CHECK-002 schemas valid JSON Schema")
    print("- CHECK-003 artifact files match their schemas")
    print("- INV-001 requirement references resolve")
    print("- INV-002 approved decisions have rationale")
    print("- INV-003 superseded artifacts identify valid successors")
    print("- INV-004 DONE tasks are not verification FAILED")
    print("- INV-005 approved requirements have verification methods")
    print("- INV-006 persistent IDs are unique")
    print("- INV-007 decision supersession is reciprocal")
    print("- INV-008 no obvious secrets detected")
    print("- INV-011 PASSED verification has evidence")
    print("- INV-012 DOING tasks have owners")
    print("- INV-013 PROMOTED queue items target valid tasks")
    print("- INV-014 diagnostic root-cause state is coherent")
    print("- INV-015 state projection references resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
