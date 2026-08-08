"""Application use case for complete repository governance compliance."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from ai_governance.application.governance_validation import validate_governance_artifacts
from ai_governance.application.schema_validation import (
    build_validators,
    validate_artifacts,
    validate_schema_definition,
)
from ai_governance.domain.artifacts import Artifact
from ai_governance.domain.findings import Finding


@dataclass(frozen=True, slots=True)
class RepositoryComplianceSnapshot:
    """Repository data prepared by infrastructure for compliance evaluation."""

    artifacts: tuple[Artifact, ...]
    schemas: Mapping[str, dict[str, Any]]
    preflight_findings: tuple[Finding, ...] = ()
    security_findings: tuple[Finding, ...] = ()


def evaluate_repository_compliance(
    snapshot: RepositoryComplianceSnapshot,
) -> list[Finding]:
    """Evaluate repository compliance without direct filesystem access."""

    findings = list(snapshot.preflight_findings)

    valid_schemas: dict[str, dict[str, Any]] = {}
    for kind, schema in snapshot.schemas.items():
        issues = validate_schema_definition(schema)
        if issues:
            for issue in issues:
                findings.append(
                    Finding(
                        code="CHECK-002",
                        message=issue,
                        rule="schema-definition",
                        context={"artifact_kind": kind},
                    )
                )
        else:
            valid_schemas[kind] = schema

    if valid_schemas:
        validators = build_validators(valid_schemas)
        structurally_validatable: Iterable[Artifact] = (
            artifact for artifact in snapshot.artifacts if artifact.kind in validators
        )
        findings.extend(validate_artifacts(structurally_validatable, validators))

    findings.extend(validate_governance_artifacts(snapshot.artifacts))
    findings.extend(snapshot.security_findings)
    return findings
