from ai_governance.domain.artifacts import Artifact
from ai_governance.domain.invariants import find_duplicate_ids


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
