"""Filesystem adapter that prepares repository data for compliance evaluation."""

from __future__ import annotations

from pathlib import Path

from ai_governance.application.repository_compliance import (
    RepositoryComplianceSnapshot,
    SchemaContract,
)
from ai_governance.domain.findings import Finding
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


def load_repository_compliance_snapshot(
    repository_root: Path,
) -> RepositoryComplianceSnapshot:
    """Read repository state without evaluating application/domain policy."""

    findings: list[Finding] = []

    for path in required_paths(repository_root):
        if not path.exists():
            relative = str(path.relative_to(repository_root))
            findings.append(
                Finding(
                    code="CHECK-001",
                    message=f"missing required file: {relative}",
                    source=relative,
                    rule="required-file",
                )
            )

    schemas: dict[str, SchemaContract] = {}
    for kind, path in schema_paths(repository_root).items():
        relative = str(path.relative_to(repository_root))
        try:
            schemas[kind] = SchemaContract(data=load_json_schema(path), source=relative)
        except Exception as exc:
            findings.append(
                Finding(
                    code="CHECK-002",
                    message=f"invalid schema {relative}: {exc}",
                    source=relative,
                    rule="schema-load",
                    context={"artifact_kind": kind},
                )
            )

    artifacts = []
    loaded, load_issues = load_artifact_documents(
        artifact_roots(repository_root), SUPPORTED_DOCUMENT_SUFFIXES
    )
    for issue in load_issues:
        relative = str(issue.path.relative_to(repository_root))
        findings.append(
            Finding(
                code="CHECK-003",
                message=f"cannot parse {relative}: {issue.error}",
                source=relative,
                rule="artifact-parse",
            )
        )

    for loaded_artifact in loaded:
        path = loaded_artifact.path
        relative = str(path.relative_to(repository_root))
        if not isinstance(loaded_artifact.data, dict):
            findings.append(
                Finding(
                    code="CHECK-003",
                    message=f"artifact must be an object: {relative}",
                    source=relative,
                    rule="artifact-object",
                )
            )
            continue
        artifacts.append(
            domain_artifact(
                kind=loaded_artifact.kind,
                path=path,
                data=loaded_artifact.data,
                repository_root=repository_root,
            )
        )

    return RepositoryComplianceSnapshot(
        artifacts=tuple(artifacts),
        schemas=schemas,
        preflight_findings=tuple(findings),
        security_findings=tuple(scan_obvious_secrets(repository_root)),
    )
