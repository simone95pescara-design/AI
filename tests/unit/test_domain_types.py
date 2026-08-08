from ai_governance.domain.artifacts import Artifact
from ai_governance.domain.findings import Finding
from ai_governance.domain.references import Reference


def test_artifact_exposes_string_persistent_id() -> None:
    artifact = Artifact(kind="REQ", data={"id": "REQ-001", "status": "APPROVED"}, source="requirements/REQ-001.yaml")

    assert artifact.artifact_id == "REQ-001"
    assert artifact.source == "requirements/REQ-001.yaml"


def test_artifact_rejects_non_string_id_as_domain_identity() -> None:
    artifact = Artifact(kind="REQ", data={"id": 1})

    assert artifact.artifact_id is None


def test_reference_carries_expected_target_contract_without_resolution_side_effects() -> None:
    reference = Reference(
        target_id="REQ-001",
        expected_kind="REQ",
        source_id="DEC-001",
        field="affected_requirements",
    )

    assert reference.target_id == "REQ-001"
    assert reference.expected_kind == "REQ"
    assert reference.source_id == "DEC-001"
    assert reference.field == "affected_requirements"


def test_finding_is_transport_neutral_structured_result() -> None:
    finding = Finding(
        code="SCHEMA-STRUCTURE",
        message="id must be a string",
        source="requirements/REQ-001.yaml",
        location="id",
    )

    assert finding.code == "SCHEMA-STRUCTURE"
    assert finding.source == "requirements/REQ-001.yaml"
    assert finding.location == "id"
