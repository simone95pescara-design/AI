"""Application service for structural JSON Schema validation.

This module validates artifact structure against schema data supplied by callers.
It does not read the repository, evaluate governance invariants or semantic relationships.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator


@dataclass(frozen=True, slots=True)
class SchemaIssue:
    """One deterministic structural validation finding."""

    path: Path
    location: str
    message: str


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

    return {
        kind: Draft202012Validator(schema)
        for kind, schema in schemas.items()
    }


def validate_artifact_documents(
    documents: Iterable[tuple[str, Path, dict[str, Any]]],
    validators: dict[str, Draft202012Validator],
) -> list[SchemaIssue]:
    """Return deterministic structural issues for parsed artifact objects."""

    issues: list[SchemaIssue] = []
    for kind, path, data in documents:
        schema_errors = sorted(
            validators[kind].iter_errors(data),
            key=lambda item: list(item.absolute_path),
        )
        for error in schema_errors:
            location = ".".join(str(part) for part in error.absolute_path) or "<root>"
            issues.append(SchemaIssue(path=path, location=location, message=error.message))
    return issues
