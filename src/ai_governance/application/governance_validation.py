"""Application orchestration for governance-domain validation."""

from __future__ import annotations

from collections.abc import Iterable

from ai_governance.domain.artifact_index import ArtifactIndex
from ai_governance.domain.artifacts import Artifact
from ai_governance.domain.findings import Finding
from ai_governance.domain.invariants import (
    find_approved_decisions_without_rationale,
    find_approved_requirements_without_verification_method,
    find_done_tasks_with_failed_verification,
    find_duplicate_ids,
    find_invalid_supersession_successors,
    find_missing_requirement_references,
    find_nonreciprocal_decision_supersessions,
)


def validate_semantics(artifacts: Iterable[Artifact]) -> list[Finding]:
    """Run semantic governance rules while preserving legacy finding order."""

    artifact_list = list(artifacts)
    index = ArtifactIndex.from_artifacts(artifact_list)
    findings: list[Finding] = []

    for artifact in artifact_list:
        if artifact.kind == "DEC":
            findings.extend(find_approved_decisions_without_rationale([artifact]))
            findings.extend(find_invalid_supersession_successors([artifact], index))
            findings.extend(find_nonreciprocal_decision_supersessions([artifact], index))

        if artifact.kind == "REQ":
            findings.extend(find_approved_requirements_without_verification_method([artifact]))
            findings.extend(find_invalid_supersession_successors([artifact], index))

        findings.extend(find_done_tasks_with_failed_verification([artifact]))
        findings.extend(find_missing_requirement_references([artifact], index))

    return findings


def validate_governance_artifacts(artifacts: Iterable[Artifact]) -> list[Finding]:
    """Run all domain-level governance checks in baseline order."""

    artifact_list = list(artifacts)
    return [*find_duplicate_ids(artifact_list), *validate_semantics(artifact_list)]
