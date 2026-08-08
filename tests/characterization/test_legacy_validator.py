import importlib.util
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("legacy_governance_validate", REPO / "compliance" / "validate.py")
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def artifact(kind, path, data):
    return (kind, Path(path), data)


def test_legacy_cli_pass_contract_on_current_repository():
    result = subprocess.run(
        [sys.executable, str(REPO / "compliance" / "validate.py")],
        cwd=REPO,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert result.stderr == ""
    assert "COMPLIANCE: PASS" in result.stdout
    for code in [
        "CHECK-001",
        "CHECK-002",
        "CHECK-003",
        "INV-001",
        "INV-002",
        "INV-003",
        "INV-004",
        "INV-005",
        "INV-006",
        "INV-007",
        "INV-008",
    ]:
        assert code in result.stdout


def test_legacy_duplicate_id_contract():
    errors = []
    artifacts = [
        artifact("DEC", "decisions/DEC-001.yaml", {"id": "DEC-001"}),
        artifact("DEC", "decisions/DEC-duplicate.yaml", {"id": "DEC-001"}),
    ]

    validator.check_duplicate_ids(artifacts, errors)

    assert len(errors) == 1
    assert errors[0].startswith("INV-006: duplicate ID DEC-001:")


def test_legacy_reference_resolution_only_enforces_requirement_ids():
    errors = validator.validate_semantics([
        artifact(
            "DEC",
            "decisions/DEC-001.yaml",
            {
                "id": "DEC-001",
                "status": "APPROVED",
                "rationale": "reason",
                "affected_items": ["REQ-404", "DEC-404", "RISK-404"],
            },
        )
    ])

    assert any(error.startswith("INV-001:") and "REQ-404" in error for error in errors)
    assert not any("DEC-404" in error for error in errors)
    assert not any("RISK-404" in error for error in errors)


def test_legacy_decision_approval_contract():
    errors = validator.validate_semantics([
        artifact(
            "DEC",
            "decisions/DEC-001.yaml",
            {"id": "DEC-001", "status": "APPROVED", "rationale": ""},
        )
    ])

    assert errors == [
        "INV-002: approved decision DEC-001 has no rationale (decisions/DEC-001.yaml)"
    ]


def test_legacy_requirement_approval_contract():
    errors = validator.validate_semantics([
        artifact(
            "REQ",
            "requirements/REQ-001.yaml",
            {
                "id": "REQ-001",
                "status": "APPROVED",
                "verification_method": "",
            },
        )
    ])

    assert errors == [
        "INV-005: approved requirement REQ-001 has no verification_method (requirements/REQ-001.yaml)"
    ]


def test_legacy_state_done_failed_contract():
    errors = validator.validate_semantics([
        artifact(
            "STATE",
            "state/current.yaml",
            {
                "status": "ACTIVE",
                "tasks": [
                    {
                        "id": "TASK-001",
                        "status": "DONE",
                        "verification_status": "FAILED",
                    }
                ],
            },
        )
    ])

    assert errors == [
        "INV-004: task TASK-001 is DONE with FAILED verification (state/current.yaml)"
    ]


def test_legacy_secret_scanner_contract(tmp_path, monkeypatch):
    fake_secret = "gh" + "p_" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456"
    secret_file = tmp_path / "sample.txt"
    secret_file.write_text(fake_secret, encoding="utf-8")
    ignored = tmp_path / "sample.bin"
    ignored.write_text(fake_secret, encoding="utf-8")

    monkeypatch.setattr(validator, "REPO", tmp_path)
    errors = []
    validator.check_obvious_secrets(errors)

    assert errors == ["INV-008: possible secret in sample.txt"]


def test_legacy_extract_references_contract():
    value = {
        "text": "DEC-001 REQ-002 RISK-003 TASK-004",
        "nested": ["REQ-005", {"value": "DEC-006"}],
    }

    assert validator.extract_references(value) == {
        "DEC-001",
        "REQ-002",
        "RISK-003",
        "REQ-005",
        "DEC-006",
    }
