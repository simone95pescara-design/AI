from ai_governance.domain.artifact_index import ArtifactIndex
from ai_governance.domain.artifacts import Artifact
from ai_governance.domain.invariants import (
    find_approved_requirements_without_verification_method,
    find_duplicate_ids,
    find_invalid_supersession_successors,
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


def test_artifact_index_excludes_state_and_preserves_legacy_last_wins_lookup() -> None:
    first = Artifact(kind="DEC", data={"id": "DEC-001"}, source="decisions/first.yaml")
    second = Artifact(kind="DEC", data={"id": "DEC-001"}, source="decisions/second.yaml")
    state = Artifact(kind="STATE", data={"id": "DEC-002"}, source="state/current.yaml")

    index = ArtifactIndex.from_artifacts([first, state, second])

    assert index.get("DEC-001") is second
    assert index.get("DEC-002") is None


def test_superseded_decision_requires_successor() -> None:
    artifact = Artifact(
        kind="DEC",
        data={"id": "DEC-001", "status": "SUPERSEDED", "superseded_by": None},
        source="decisions/DEC-001.yaml",
    )
    index = ArtifactIndex.from_artifacts([artifact])

    findings = find_invalid_supersession_successors([artifact], index)

    assert len(findings) == 1
    assert findings[0].code == "INV-003"
    assert findings[0].message == (
        "superseded decision DEC-001 must declare superseded_by (decisions/DEC-001.yaml)"
    )


def test_superseded_decision_rejects_missing_self_or_wrong_kind_successor() -> None:
    wrong_kind = Artifact(
        kind="REQ",
        data={"id": "REQ-001", "status": "APPROVED"},
        source="requirements/REQ-001.yaml",
    )
    cases = ["DEC-404", "DEC-001", "REQ-001"]

    for successor in cases:
        artifact = Artifact(
            kind="DEC",
            data={"id": "DEC-001", "status": "SUPERSEDED", "superseded_by": successor},
            source="decisions/DEC-001.yaml",
        )
        index = ArtifactIndex.from_artifacts([artifact, wrong_kind])
        findings = find_invalid_supersession_successors([artifact], index)
        assert len(findings) == 1
        assert findings[0].message == (
            f"superseded decision DEC-001 points to invalid successor {successor!r} "
            "(decisions/DEC-001.yaml)"
        )


def test_superseded_requirement_accepts_valid_same_kind_successor() -> None:
    old = Artifact(
        kind="REQ",
        data={"id": "REQ-001", "status": "SUPERSEDED", "superseded_by": "REQ-002"},
        source="requirements/REQ-001.yaml",
    )
    successor = Artifact(
        kind="REQ",
        data={"id": "REQ-002", "status": "APPROVED"},
        source="requirements/REQ-002.yaml",
    )
    index = ArtifactIndex.from_artifacts([old, successor])

    assert find_invalid_supersession_successors([old], index) == []
