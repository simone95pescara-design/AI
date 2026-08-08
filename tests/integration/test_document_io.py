import json

import pytest

from ai_governance.infrastructure.document_io import load_document, load_json_schema


def test_load_json_schema_preserves_json_object(tmp_path):
    path = tmp_path / "schema.json"
    expected = {"type": "object", "required": ["id"]}
    path.write_text(json.dumps(expected), encoding="utf-8")

    assert load_json_schema(path) == expected


def test_load_document_uses_json_for_json_suffix(tmp_path):
    path = tmp_path / "artifact.json"
    path.write_text('{"id": "DEC-001", "status": "APPROVED"}', encoding="utf-8")

    assert load_document(path) == {"id": "DEC-001", "status": "APPROVED"}


def test_load_document_uses_yaml_for_yaml_suffix(tmp_path):
    path = tmp_path / "artifact.yaml"
    path.write_text("id: REQ-001\nstatus: APPROVED\n", encoding="utf-8")

    assert load_document(path) == {"id": "REQ-001", "status": "APPROVED"}


def test_load_document_preserves_parse_errors(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{not-json", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        load_document(path)
