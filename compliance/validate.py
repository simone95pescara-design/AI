from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

from ai_governance.application.schema_validation import (
    build_validators,
    validate_artifact_documents,
    validate_schema_definition,
)
from ai_governance.infrastructure.artifact_repository import load_artifact_documents
from ai_governance.infrastructure.document_io import (
    load_document as infrastructure_load_document,
    load_json_schema,
)
from ai_governance.infrastructure.repository_registry import (
    SUPPORTED_DOCUMENT_SUFFIXES,
    artifact_roots,
    required_paths,
    schema_paths,
)

REPO = Path(__file__).resolve().parents[1]
REQUIRED = required_paths(REPO)
SCHEMAS = schema_paths(REPO)
ARTIFACT_ROOTS = artifact_roots(REPO)
ID_PATTERN = re.compile(r"\b(?:DEC|REQ|RISK)-\d{3,}\b")
SUPPORTED_SUFFIXES = SUPPORTED_DOCUMENT_SUFFIXES


def fail(code: str, message: str, errors: list[str]) -> None:
    errors.append(f"{code}: {message}")


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def check_required_files(errors: list[str]) -> None:
    for path in REQUIRED:
        if not path.exists():
            fail("CHECK-001", f"missing required file: {path.relative_to(REPO)}", errors)


def load_schema(path: Path) -> dict[str, Any]:
    """Compatibility wrapper around the infrastructure schema loader."""
    return load_json_schema(path)


def check_schemas(errors: list[str]) -> None:
    for path in SCHEMAS.values():
        issues = validate_schema_definition(path)
        for issue in issues:
            if issue == "schema lacks object/required contract":
                fail("CHECK-002", f"schema lacks object/required contract: {path.relative_to(REPO)}", errors)
            else:
                fail("CHECK-002", f"invalid schema {path.relative_to(REPO)}: {issue}", errors)


def load_document(path: Path) -> Any:
    """Compatibility wrapper around the infrastructure document loader."""
    return infrastructure_load_document(path)


def load_artifacts(errors: list[str]) -> list[tuple[str, Path, dict[str, Any]]]:
    artifacts: list[tuple[str, Path, dict[str, Any]]] = []
    loaded, load_issues = load_artifact_documents(ARTIFACT_ROOTS, SUPPORTED_SUFFIXES)

    for issue in load_issues:
        fail(
            "CHECK-003",
            f"cannot parse {issue.path.relative_to(REPO)}: {issue.error}",
            errors,
        )

    object_documents: list[tuple[str, Path, dict[str, Any]]] = []
    for artifact in loaded:
        kind, path, data = artifact.kind, artifact.path, artifact.data
        if not isinstance(data, dict):
            fail("CHECK-003", f"artifact must be an object: {path.relative_to(REPO)}", errors)
            continue
        object_documents.append((kind, path, data))
        artifacts.append((kind, path, data))

    validators = build_validators(SCHEMAS)
    for issue in validate_artifact_documents(object_documents, validators):
        fail(
            "CHECK-003",
            f"{issue.path.relative_to(REPO)} [{issue.location}]: {issue.message}",
            errors,
        )
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

        if kind == "STATE":
            for task in data.get("tasks", []) or []:
                if task.get("status") == "DONE" and task.get("verification_status") == "FAILED":
                    fail("INV-004", f"task {task.get('id', '<unknown>')} is DONE with FAILED verification ({rel})", errors)

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
    return 0


if __name__ == "__main__":
    sys.exit(main())
