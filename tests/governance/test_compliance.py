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
    result = subprocess.run([sys.executable, str(REPO / "compliance" / "validate.py")], cwd=REPO, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


def test_approved_decision_requires_rationale():
    errors = validator.validate_semantics([artifact("DEC", "decisions/DEC-001.yaml", {"id": "DEC-001", "status": "APPROVED", "rationale": ""})])
    assert any(e.startswith("INV-002:") for e in errors)


def test_general_reference_integrity():
    errors = validator.validate_semantics([artifact("DEC", "decisions/DEC-001.yaml", {"id": "DEC-001", "status": "APPROVED", "rationale": "ok", "affected_items": ["REQ-404"]})])
    assert any(e.startswith("INV-016:") for e in errors)


def test_passed_verification_requires_evidence_and_provenance():
    errors = validator.validate_semantics([artifact("VER", "verification/VER-001.yaml", {"id": "VER-001", "status": "PASSED", "evidence": [], "provenance": {}})])
    assert any(e.startswith("INV-011:") for e in errors)
    assert any(e.startswith("INV-017:") for e in errors)


def test_doing_task_requires_owner():
    errors = validator.validate_semantics([artifact("TASK", "tasks/TASK-003.yaml", {"id": "TASK-003", "status": "DOING", "verification_status": "PARTIAL", "owner": None, "dependencies": [], "blockers": []})])
    assert any(e.startswith("INV-012:") for e in errors)


def test_task_dependency_cycle_is_rejected():
    errors = validator.validate_semantics([
        artifact("TASK", "tasks/TASK-001.yaml", {"id": "TASK-001", "status": "TODO", "dependencies": ["TASK-002"], "blockers": []}),
        artifact("TASK", "tasks/TASK-002.yaml", {"id": "TASK-002", "status": "TODO", "dependencies": ["TASK-001"], "blockers": []}),
    ])
    assert any(e.startswith("INV-018:") for e in errors)


def test_queue_task_promotion_is_reciprocal():
    errors = validator.validate_semantics([
        artifact("QUEUE", "queue/QUEUE-001.yaml", {"id": "QUEUE-001", "status": "PROMOTED", "promoted_to": "TASK-001"}),
        artifact("TASK", "tasks/TASK-001.yaml", {"id": "TASK-001", "status": "TODO", "dependencies": [], "blockers": [], "queue_source": None}),
    ])
    assert any(e.startswith("INV-013:") for e in errors)


def test_closed_resolved_diagnostic_requires_verification():
    errors = validator.validate_semantics([artifact("DIA", "diagnostics/DIA-001.yaml", {"id": "DIA-001", "status": "CLOSED_RESOLVED", "root_cause_status": "CONFIRMED", "root_cause": "cause", "closure_reason": "fixed", "verification": [], "residual_risk": []})])
    assert any(e.startswith("INV-019:") for e in errors)


def test_state_projection_references_must_resolve():
    errors = validator.validate_semantics([artifact("STATE", "state/current.yaml", {"status": "ACTIVE", "active_tasks": ["TASK-999"], "queued_work": [], "open_diagnostics": []})])
    assert any(e.startswith("INV-015:") for e in errors)
