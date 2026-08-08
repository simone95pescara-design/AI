from ai_governance.application.governance_validation import (
    validate_governance_artifacts,
    validate_semantics,
)
from ai_governance.domain.artifacts import Artifact


def test_semantic_orchestration_preserves_per_artifact_legacy_order() -> None:
    decision = Artifact(
        kind="DEC",
        data={
            "id": "DEC-002",
            "status": "APPROVED",
            "rationale": "",
            "supersedes": ["DEC-404"],
            "affected_items": ["REQ-404"],
        },
        source="decisions/DEC-002.yaml",
    )

    findings = validate_semantics([decision])

    assert [finding.code for finding in findings] == ["INV-002", "INV-007", "INV-001"]


def test_governance_orchestration_runs_duplicate_check_before_semantics() -> None:
    artifacts = [
        Artifact(
            kind="DEC",
            data={"id": "DEC-001", "status": "APPROVED", "rationale": "reason"},
            source="decisions/DEC-001.yaml",
        ),
        Artifact(
            kind="DEC",
            data={"id": "DEC-001", "status": "APPROVED", "rationale": ""},
            source="decisions/DEC-copy.yaml",
        ),
    ]

    findings = validate_governance_artifacts(artifacts)

    assert [finding.code for finding in findings] == ["INV-006", "INV-002"]


def test_semantic_orchestration_uses_shared_index_across_artifacts() -> None:
    requirement = Artifact(
        kind="REQ",
        data={
            "id": "REQ-001",
            "status": "APPROVED",
            "verification_method": "test",
        },
        source="requirements/REQ-001.yaml",
    )
    decision = Artifact(
        kind="DEC",
        data={
            "id": "DEC-001",
            "status": "APPROVED",
            "rationale": "reason",
            "affected_items": ["REQ-001"],
        },
        source="decisions/DEC-001.yaml",
    )

    assert validate_semantics([decision, requirement]) == []
