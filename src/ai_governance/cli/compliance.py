"""Composition root and CLI for repository governance compliance."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ai_governance.application.governance_validation import validate_governance_artifacts
from ai_governance.application.schema_validation import (
    build_validators,
    validate_artifacts,
    validate_schema_definition,
)
from ai_governance.infrastructure.artifact_mapping import domain_artifact
from ai_governance.infrastructure.artifact_repository import load_artifact_documents
from ai_governance.infrastructure.document_io import load_json_schema
from ai_governance.infrastructure.repository_registry import (
    SUPPORTED_DOCUMENT_SUFFIXES,
    artifact_roots,
    required_paths,
    schema_paths,
)
from ai_governance.infrastructure.security_scan import scan_obvious_secrets

PASS_LINES = (
    "CHECK-001 required governance files present",
    "CHECK-002 schemas valid JSON Schema",
    "CHECK-003 artifact files match their schemas",
    "INV-001 requirement references resolve",
    "INV-002 approved decisions have rationale",
    "INV-003 superseded artifacts identify valid successors",
    "INV-004 DONE tasks are not verification FAILED",
    "INV-005 approved requirements have verification methods",
    "INV-006 persistent IDs are unique",
    "INV-007 decision supersession is reciprocal",
    "INV-008 no obvious secrets detected",
)


def required_file_errors(repository_root: Path) -> list[str]:
    return [
        f"CHECK-001: missing required file: {path.relative_to(repository_root)}"
        for path in required_paths(repository_root)
        if not path.exists()
    ]


def schema_errors(repository_root: Path) -> list[str]:
    errors: list[str] = []
    for path in schema_paths(repository_root).values():
        try:
            schema = load_json_schema(path)
        except Exception as exc:
            errors.append(
                f"CHECK-002: invalid schema {path.relative_to(repository_root)}: {exc}"
            )
            continue

        for issue in validate_schema_definition(schema):
            if issue == "schema lacks object/required contract":
                errors.append(
                    "CHECK-002: schema lacks object/required contract: "
                    f"{path.relative_to(repository_root)}"
                )
            else:
                errors.append(
                    f"CHECK-002: invalid schema {path.relative_to(repository_root)}: {issue}"
                )
    return errors


def load_and_validate_artifacts(
    repository_root: Path,
) -> tuple[list[tuple[str, Path, dict[str, Any]]], list[object], list[str]]:
    legacy_artifacts: list[tuple[str, Path, dict[str, Any]]] = []
    domain_artifacts: list[object] = []
    errors: list[str] = []

    loaded, load_issues = load_artifact_documents(
        artifact_roots(repository_root), SUPPORTED_DOCUMENT_SUFFIXES
    )
    for issue in load_issues:
        errors.append(
            "CHECK-003: cannot parse "
            f"{issue.path.relative_to(repository_root)}: {issue.error}"
        )

    for loaded_artifact in loaded:
        kind, path, data = loaded_artifact.kind, loaded_artifact.path, loaded_artifact.data
        if not isinstance(data, dict):
            errors.append(
                f"CHECK-003: artifact must be an object: {path.relative_to(repository_root)}"
            )
            continue
        domain_artifacts.append(
            domain_artifact(
                kind=kind,
                path=path,
                data=data,
                repository_root=repository_root,
            )
        )
        legacy_artifacts.append((kind, path, data))

    schemas = {
        kind: load_json_schema(path)
        for kind, path in schema_paths(repository_root).items()
    }
    validators = build_validators(schemas)
    for finding in validate_artifacts(domain_artifacts, validators):
        source = finding.source or "<unknown>"
        location = finding.location or "<root>"
        errors.append(f"CHECK-003: {source} [{location}]: {finding.message}")

    return legacy_artifacts, domain_artifacts, errors


def repository_errors(repository_root: Path) -> list[str]:
    """Run the complete repository compliance pipeline and return legacy-formatted errors."""

    errors = required_file_errors(repository_root)
    errors.extend(schema_errors(repository_root))
    _, domain_artifacts, artifact_errors = load_and_validate_artifacts(repository_root)
    errors.extend(artifact_errors)
    for finding in validate_governance_artifacts(domain_artifacts):
        errors.append(f"{finding.code}: {finding.message}")
    for finding in scan_obvious_secrets(repository_root):
        errors.append(f"{finding.code}: {finding.message}")
    return errors


def main(repository_root: Path | None = None) -> int:
    root = repository_root or Path(__file__).resolve().parents[3]
    errors = repository_errors(root)
    if errors:
        print("COMPLIANCE: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("COMPLIANCE: PASS")
    for line in PASS_LINES:
        print(f"- {line}")
    return 0
