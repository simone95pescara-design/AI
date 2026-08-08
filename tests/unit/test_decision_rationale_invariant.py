from ai_governance.domain.artifacts import Artifact
from ai_governance.domain.invariants import find_approved_decisions_without_rationale


def test_approved_decision_without_rationale_returns_inv_002() -> None:
    artifact = Artifact(
        kind="DEC",
        data={"id": "DEC-101", "status": "APPROVED", "rationale": ""},
        source="decisions/DEC-101.yaml",
    )

    findings = find_approved_decisions_without_rationale([artifact])

    assert len(findings) == 1
    assert findings[0].code == "INV-002"
    assert findings[0].message == (
        "approved decision DEC-101 has no rationale (decisions/DEC-101.yaml)"
    )
    assert findings[0].source == "decisions/DEC-101.yaml"
    assert findings[0].location == "rationale"


def test_approved_decision_with_nonempty_rationale_passes() -> None:
    artifact = Artifact(
        kind="DEC",
        data={"id": "DEC-101", "status": "APPROVED", "rationale": "because"},
        source="decisions/DEC-101.yaml",
    )

    assert find_approved_decisions_without_rationale([artifact]) == []


def test_nonapproved_or_nondecision_artifacts_are_out_of_scope() -> None:
    artifacts = [
        Artifact(
            kind="DEC",
            data={"id": "DEC-101", "status": "PROPOSED", "rationale": ""},
            source="decisions/DEC-101.yaml",
        ),
        Artifact(
            kind="REQ",
            data={"id": "REQ-101", "status": "APPROVED", "rationale": ""},
            source="requirements/REQ-101.yaml",
        ),
    ]

    assert find_approved_decisions_without_rationale(artifacts) == []
