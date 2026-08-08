from ai_governance.application.schema_validation import (
    build_validators,
    validate_artifacts,
    validate_schema_definition,
)
from ai_governance.domain.artifacts import Artifact


def test_validate_schema_definition_accepts_object_schema() -> None:
    schema = {
        "type": "object",
        "required": ["id"],
        "properties": {"id": {"type": "string"}},
    }

    assert validate_schema_definition(schema) == []


def test_validate_schema_definition_rejects_missing_required_contract() -> None:
    schema = {
        "type": "object",
        "properties": {"id": {"type": "string"}},
    }

    assert validate_schema_definition(schema) == ["schema lacks object/required contract"]


def test_validate_artifacts_preserves_source_location_and_message() -> None:
    schema = {
        "type": "object",
        "required": ["id"],
        "properties": {
            "id": {"type": "string"},
            "status": {"type": "string"},
        },
    }
    validators = build_validators({"REQ": schema})
    findings = validate_artifacts(
        [Artifact(kind="REQ", source="requirements/REQ-001.yaml", data={"id": 7, "status": "APPROVED"})],
        validators,
    )

    assert len(findings) == 1
    assert findings[0].code == "CHECK-003"
    assert findings[0].source == "requirements/REQ-001.yaml"
    assert findings[0].location == "id"
    assert findings[0].message == "7 is not of type 'string'"
