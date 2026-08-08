from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from ai_governance.application.governance_validation import (
    validate_semantics as application_validate_semantics,
)
from ai_governance.cli.compliance import (
    load_and_validate_artifacts,
    main as compliance_main,
    required_file_errors,
    schema_errors,
)
from ai_governance.domain.artifacts import Artifact
from ai_governance.domain.invariants import find_duplicate_ids
from ai_governance.domain.references import extract_persistent_reference_ids
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
from ai_governance.infrastructure.security_scan import scan_obvious_secrets

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
    """Legacy compatibility wrapper."""
    errors.extend(required_file_errors(REPO))


def load_schema(path: Path) -> dict[str, Any]:
    """Legacy compatibility wrapper."""
    return load_json_schema(path)


def check_schemas(errors: list[str]) -> None:
    """Legacy compatibility wrapper."""
    errors.extend(schema_errors(REPO))


def load_document(path: Path) -> Any:
    """Legacy compatibility wrapper."""
    return infrastructure_load_document(path)


def load_artifacts(errors: list[str]) -> list[tuple[str, Path, dict[str, Any]]]:
    """Legacy compatibility wrapper."""
    artifacts, _, findings = load_and_validate_artifacts(REPO)
    errors.extend(findings)
    return artifacts


def _domain_artifacts(
    artifacts: list[tuple[str, Path, dict[str, Any]]],
) -> list[Artifact]:
    return [
        Artifact(
            kind=kind,
            data=data,
            source=str(path.relative_to(REPO)) if path.is_absolute() else str(path),
        )
        for kind, path, data in artifacts
    ]


def check_duplicate_ids(
    artifacts: list[tuple[str, Path, dict[str, Any]]], errors: list[str]
) -> None:
    """Legacy compatibility wrapper."""
    for finding in find_duplicate_ids(_domain_artifacts(artifacts)):
        fail(finding.code, finding.message, errors)


def extract_references(value: Any) -> set[str]:
    """Legacy compatibility wrapper."""
    return extract_persistent_reference_ids(value)


def validate_semantics(artifacts: list[tuple[str, Path, dict[str, Any]]]) -> list[str]:
    """Legacy compatibility wrapper."""
    return [
        f"{finding.code}: {finding.message}"
        for finding in application_validate_semantics(_domain_artifacts(artifacts))
    ]


def check_obvious_secrets(errors: list[str]) -> None:
    """Legacy compatibility wrapper."""
    for finding in scan_obvious_secrets(REPO):
        fail(finding.code, finding.message, errors)


def main() -> int:
    return compliance_main(REPO)


if __name__ == "__main__":
    sys.exit(main())
