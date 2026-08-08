from ai_governance.domain.artifacts import Artifact
from ai_governance.domain.invariants import (
    find_approved_requirements_without_verification_method,
    find_duplicate_ids,
)


def test_duplicate_id_invariant_reports_second_persistent_artifact() -> None:
    artifacts = [
        Artifact(kind="DEC", data={"id": "DEC-001"}, source="decisions/DEC-001.yaml"),
        Artifact(kind="DEC", data={"id": "DEC-001"}, source="decisions/DEC-copy.yaml"),
    ]

    findings = find_duplicate_ids(artifacts)

    assert len(findings) == 1
    assert findings[0].code == "INV-006"
    assert findings[0].message == (
        "duplicate ID DEC-001: decisions/DEC-001.yaml and decisions/DEC-copy.yaml"
    )
    assert findings[0].source == "decisions/DEC-copy.yaml"


def test_duplicate_id_invariant_ignores_state_projection_ids() -> None:
    artifacts = [
        Artifact(kind="STATE", data={"id": "REQ-001"}, source="state/current.yaml"),
        Artifact(kind="REQ", data={"id": "REQ-001"}, source="requirements/REQ-001.yaml"),
    ]

    assert find_duplicate_ids(artifacts) == []


def test_duplicate_id_invariant_ignores_missing_or_non_string_ids() -> None:
    artifacts = [
        Artifact(kind="REQ", data={}, source="requirements/no-id.yaml"),
        Artifact(kind="REQ", data={"id": 7}, source="requirements/numeric-id.yaml"),
    ]

    assert find_duplicate_ids(artifacts) == []


def test_approved_requirement_requires_verification_method() -> None:
    artifact = Artifact(
        kind="REQ",
        data={"id": "REQ-001", "status": "APPROVED", "verification_method": ""},
        source="requirements/REQ-001.yaml",
    )

    findings = find_approved_requirements_without_verification_method([artifact])

    assert len(findings) == 1
    assert findings[0].code == "INV-005"
    assert findings[0].message == (
        "approved requirement REQ-001 has no verification_method (requirements/REQ-001.yaml)"
    )
    assert findings[0].source == "requirements/REQ-001.yaml"
    assert findings[0].location == "verification_method"


def test_non_approved_or_verified_requirement_does_not_trigger_inv_005() -> None:
    artifacts = [
        Artifact(
            kind="REQ",
            data={"id": "REQ-001", "status": "PROPOSED", "verification_method": ""},
            source="requirements/REQ-001.yaml",
        ),
        Artifact(
            kind="REQ",
            data={"id": "REQ-002", "status": "APPROVED", "verification_method": "test"},
            source="requirements/REQ-002.yaml",
        ),
        Artifact(
            kind="DEC",
            data={"id": "DEC-001", "status": "APPROVED"},
            source="decisions/DEC-001.yaml",
        ),
    ]

    assert find_approved_requirements_without_verification_method(artifacts) == []
