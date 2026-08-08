import importlib.util
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("governance_validate", REPO / "compliance" / "validate.py")
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def artifact(kind, path, data):
    return (kind, Path(path), data)


def test_compliance_validator_passes_on_repository():
    result = subprocess.run(
        [sys.executable, str(REPO / "compliance" / "validate.py")],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "COMPLIANCE: PASS" in result.stdout


def test_approved_decision_requires_rationale():
    errors = validator.validate_semantics([
        artifact("DEC", "decisions/DEC-001.yaml", {"id": "DEC-001", "status": "APPROVED", "rationale": ""})
    ])
    assert any(error.startswith("INV-002:") for error in errors)


def test_approved_requirement_requires_verification_method():
    errors = validator.validate_semantics([
        artifact("REQ", "requirements/REQ-001.yaml", {"id": "REQ-001", "status": "APPROVED", "verification_method": ""})
    ])
    assert any(error.startswith("INV-005:") for error in errors)


def test_superseded_artifact_requires_valid_successor():
    errors = validator.validate_semantics([
        artifact("DEC", "decisions/DEC-001.yaml", {"id": "DEC-001", "status": "SUPERSEDED", "superseded_by": "DEC-999"})
    ])
    assert any(error.startswith("INV-003:") for error in errors)


def test_decision_supersession_must_be_reciprocal():
    artifacts = [
        artifact("DEC", "decisions/DEC-001.yaml", {
            "id": "DEC-001", "status": "SUPERSEDED", "superseded_by": "DEC-002", "supersedes": []
        }),
        artifact("DEC", "decisions/DEC-002.yaml", {
            "id": "DEC-002", "status": "APPROVED", "rationale": "better option", "supersedes": ["DEC-001"]
        }),
    ]
    errors = validator.validate_semantics(artifacts)
    assert not any(error.startswith("INV-003:") or error.startswith("INV-007:") for error in errors)


def test_done_task_cannot_have_failed_verification():
    errors = validator.validate_semantics([
        artifact("STATE", "state/current.yaml", {
            "status": "ACTIVE",
            "tasks": [{"id": "TASK-001", "status": "DONE", "verification_status": "FAILED"}],
        })
    ])
    assert any(error.startswith("INV-004:") for error in errors)


def test_requirement_references_must_resolve():
    errors = validator.validate_semantics([
        artifact("DEC", "decisions/DEC-001.yaml", {
            "id": "DEC-001", "status": "APPROVED", "rationale": "reason", "affected_items": ["REQ-404"]
        })
    ])
    assert any(error.startswith("INV-001:") for error in errors)
