"""Application service for structural JSON Schema validation.

This module validates domain artifacts against schema data supplied by callers.
It does not read the repository, evaluate governance invariants or semantic relationships.
"""

from __future__ import annotations

from typing import Any, Iterable

from jsonschema import Draft202012Validator

from ai_governance.domain.artifacts import Artifact
from ai_governance.domain.findings import Finding


def validate_schema_definition(schema: dict[str, Any]) -> list[str]:
    """Return structural problems in one JSON Schema definition."""

    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:
        return [str(exc)]

    if schema.get("type") != "object" or not schema.get("required"):
        return ["schema lacks object/required contract"]
    return []


def build_validators(schemas: dict[str, dict[str, Any]]) -> dict[str, Draft202012Validator]:
    """Build validators for the currently active artifact kinds."""

    return {kind: Draft202012Validator(schema) for kind, schema in schemas.items()}


def validate_artifacts(
    artifacts: Iterable[Artifact],
    validators: dict[str, Draft202012Validator],
) -> list[Finding]:
    """Return deterministic structural findings for domain artifacts."""

    findings: list[Finding] = []
    for artifact in artifacts:
        schema_errors = sorted(
            validators[artifact.kind].iter_errors(artifact.data),
            key=lambda item: list(item.absolute_path),
        )
        for error in schema_errors:
            location = ".".join(str(part) for part in error.absolute_path) or "<root>"
            findings.append(
                Finding(
                    code="CHECK-003",
                    source=artifact.source,
                    location=location,
                    message=error.message,
                )
            )
    return findings
