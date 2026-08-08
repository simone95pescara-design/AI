from pathlib import Path

from ai_governance.application.schema_validation import (
    build_validators,
    validate_artifact_documents,
    validate_schema_definition,
)


def test_validate_schema_definition_accepts_object_schema(tmp_path: Path) -> None:
    schema = tmp_path / "schema.json"
    schema.write_text('{"type":"object","required":["id"],"properties":{"id":{"type":"string"}}}', encoding="utf-8")

    assert validate_schema_definition(schema) == []


def test_validate_schema_definition_rejects_missing_required_contract(tmp_path: Path) -> None:
    schema = tmp_path / "schema.json"
    schema.write_text('{"type":"object","properties":{"id":{"type":"string"}}}', encoding="utf-8")

    assert validate_schema_definition(schema) == ["schema lacks object/required contract"]


def test_validate_artifact_documents_preserves_location_and_message(tmp_path: Path) -> None:
    schema = tmp_path / "schema.json"
    schema.write_text(
        '{"type":"object","required":["id"],"properties":{"id":{"type":"string"},"status":{"type":"string"}}}',
        encoding="utf-8",
    )
    validators = build_validators({"REQ": schema})
    artifact_path = tmp_path / "REQ-001.yaml"
    issues = validate_artifact_documents(
        [("REQ", artifact_path, {"id": 7, "status": "APPROVED"})],
        validators,
    )

    assert len(issues) == 1
    assert issues[0].path == artifact_path
    assert issues[0].location == "id"
    assert issues[0].message == "7 is not of type 'string'"
