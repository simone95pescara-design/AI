from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

from ai_governance.application.schema_validation import (
    build_validators,
    validate_artifacts,
    validate_schema_definition,
)
from ai_governance.domain.artifact_index import ArtifactIndex
from ai_governance.domain.artifacts import Artifact
from ai_governance.domain.invariants import (
    find_approved_decisions_without_rationale,
    find_approved_requirements_without_verification_method,
    find_done_tasks_with_failed_verification,
    find_duplicate_ids,
    find_invalid_supersession_successors,
    find_missing_requirement_references,
    find_nonreciprocal_decision_supersessions,
)
from ai_governance.domain.references import extract_persistent_reference_ids
from ai_governance.infrastructure.artifact_mapping import domain_artifact
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
        try:
            schema = load_schema(path)
        except Exception as exc:
            fail("CHECK-002", f"invalid schema {path.relative_to(REPO)}: {exc}", errors)
            continue
        for issue in validate_schema_definition(schema):
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

    domain_artifacts = []
    for loaded_artifact in loaded:
        kind, path, data = loaded_artifact.kind, loaded_artifact.path, loaded_artifact.data
        if not isinstance(data, dict):
            fail("CHECK-003", f"artifact must be an object: {path.relative_to(REPO)}", errors)
            continue
        domain_artifacts.append(
            domain_artifact(kind=kind, path=path, data=data, repository_root=REPO)
        )
        artifacts.append((kind, path, data))

    schemas = {kind: load_schema(path) for kind, path in SCHEMAS.items()}
    validators = build_validators(schemas)
    for finding in validate_artifacts(domain_artifacts, validators):
        source = finding.source or "<unknown>"
        location = finding.location or "<root>"
        fail("CHECK-003", f"{source} [{location}]: {finding.message}", errors)
    return artifacts


def check_duplicate_ids(artifacts: list[tuple[str, Path, dict[str, Any]]], errors: list[str]) -> None:
    """Compatibility wrapper delegating INV-006 to the domain invariant."""

    domain_artifacts = [
        Artifact(
            kind=kind,
            data=data,
            source=str(path.relative_to(REPO)) if path.is_absolute() else str(path),
        )
        for kind, path, data in artifacts
    ]
    for finding in find_duplicate_ids(domain_artifacts):
        fail(finding.code, finding.message, errors)


def extract_references(value: Any) -> set[str]:
    """Compatibility wrapper around domain persistent-reference parsing."""
    return extract_persistent_reference_ids(value)


def validate_semantics(artifacts: list[tuple[str, Path, dict[str, Any]]]) -> list[str]:
    errors: list[str] = []
    domain_artifacts: list[Artifact] = []
    for kind, path, data in artifacts:
        rel = path.relative_to(REPO) if path.is_absolute() else path
        domain_artifacts.append(Artifact(kind=kind, data=data, source=str(rel)))

    artifact_index = ArtifactIndex.from_artifacts(domain_artifacts)

    for kind, path, data in artifacts:
        rel = path.relative_to(REPO) if path.is_absolute() else path
        current_artifact = Artifact(kind=kind, data=data, source=str(rel))

        if kind == "DEC":
            for finding in find_approved_decisions_without_rationale([current_artifact]):
                fail(finding.code, finding.message, errors)
            for finding in find_invalid_supersession_successors([current_artifact], artifact_index):
                fail(finding.code, finding.message, errors)
            for finding in find_nonreciprocal_decision_supersessions([current_artifact], artifact_index):
                fail(finding.code, finding.message, errors)

        if kind == "REQ":
            for finding in find_approved_requirements_without_verification_method([current_artifact]):
                fail(finding.code, finding.message, errors)
            for finding in find_invalid_supersession_successors([current_artifact], artifact_index):
                fail(finding.code, finding.message, errors)

        for finding in find_done_tasks_with_failed_verification([current_artifact]):
            fail(finding.code, finding.message, errors)

        for finding in find_missing_requirement_references([current_artifact], artifact_index):
            fail(finding.code, finding.message, errors)

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
