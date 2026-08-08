import subprocess
import sys
from pathlib import Path

from ai_governance.application.governance_validation import validate_semantics
from ai_governance.domain.artifacts import Artifact

REPO = Path(__file__).resolve().parents[2]


def artifact(kind, path, data):
    return Artifact(kind=kind, data=data, source=str(path))


def errors(artifacts):
    return [f"{finding.code}: {finding.message}" for finding in validate_semantics(artifacts)]


def test_compliance_validator_passes_on_repository():
    result = subprocess.run(
        [sys.executable, "-m", "ai_governance.cli.compliance"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "COMPLIANCE: PASS" in result.stdout


def test_approved_decision_requires_rationale():
    result = errors([artifact("DEC", "decisions/DEC-001.yaml", {"id": "DEC-001", "status": "APPROVED", "rationale": ""})])
    assert any(item.startswith("INV-002:") for item in result)


def test_approved_requirement_requires_verification_method():
    result = errors([artifact("REQ", "requirements/REQ-001.yaml", {"id": "REQ-001", "status": "APPROVED", "verification_method": ""})])
    assert any(item.startswith("INV-005:") for item in result)


def test_superseded_artifact_requires_valid_successor():
    result = errors([artifact("DEC", "decisions/DEC-001.yaml", {"id": "DEC-001", "status": "SUPERSEDED", "superseded_by": "DEC-999"})])
    assert any(item.startswith("INV-003:") for item in result)


def test_decision_supersession_must_be_reciprocal():
    artifacts = [
        artifact("DEC", "decisions/DEC-001.yaml", {"id": "DEC-001", "status": "SUPERSEDED", "superseded_by": "DEC-002", "supersedes": []}),
        artifact("DEC", "decisions/DEC-002.yaml", {"id": "DEC-002", "status": "APPROVED", "rationale": "better option", "supersedes": ["DEC-001"]}),
    ]
    result = errors(artifacts)
    assert not any(item.startswith("INV-003:") or item.startswith("INV-007:") for item in result)


def test_done_task_cannot_have_failed_verification():
    result = errors([artifact("STATE", "state/current.yaml", {"status": "ACTIVE", "tasks": [{"id": "TASK-001", "status": "DONE", "verification_status": "FAILED"}]})])
    assert any(item.startswith("INV-004:") for item in result)


def test_requirement_references_must_resolve():
    result = errors([artifact("DEC", "decisions/DEC-001.yaml", {"id": "DEC-001", "status": "APPROVED", "rationale": "reason", "affected_items": ["REQ-404"]})])
    assert any(item.startswith("INV-001:") for item in result)
