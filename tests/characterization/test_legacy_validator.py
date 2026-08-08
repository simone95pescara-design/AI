import subprocess
import sys
from pathlib import Path

from ai_governance.application.governance_validation import validate_semantics
from ai_governance.domain.artifacts import Artifact
from ai_governance.domain.invariants import find_duplicate_ids
from ai_governance.domain.references import extract_persistent_reference_ids
from ai_governance.infrastructure.security_scan import scan_obvious_secrets

REPO = Path(__file__).resolve().parents[2]


def artifact(kind, path, data):
    return Artifact(kind=kind, data=data, source=str(path))


def errors(artifacts):
    return [f"{finding.code}: {finding.message}" for finding in validate_semantics(artifacts)]


def test_cli_pass_contract_on_current_repository():
    result = subprocess.run(
        [sys.executable, "-m", "ai_governance.cli.compliance"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert result.stderr == ""
    assert "COMPLIANCE: PASS" in result.stdout
    for code in ["CHECK-001", "CHECK-002", "CHECK-003", "INV-001", "INV-002", "INV-003", "INV-004", "INV-005", "INV-006", "INV-007", "INV-008"]:
        assert code in result.stdout


def test_duplicate_id_contract():
    findings = find_duplicate_ids([
        artifact("DEC", "decisions/DEC-001.yaml", {"id": "DEC-001"}),
        artifact("DEC", "decisions/DEC-duplicate.yaml", {"id": "DEC-001"}),
    ])
    assert len(findings) == 1
    assert f"{findings[0].code}: {findings[0].message}".startswith("INV-006: duplicate ID DEC-001:")


def test_reference_resolution_only_enforces_requirement_ids():
    result = errors([artifact("DEC", "decisions/DEC-001.yaml", {"id": "DEC-001", "status": "APPROVED", "rationale": "reason", "affected_items": ["REQ-404", "DEC-404", "RISK-404"]})])
    assert any(item.startswith("INV-001:") and "REQ-404" in item for item in result)
    assert not any("DEC-404" in item for item in result)
    assert not any("RISK-404" in item for item in result)


def test_decision_approval_contract():
    assert errors([artifact("DEC", "decisions/DEC-001.yaml", {"id": "DEC-001", "status": "APPROVED", "rationale": ""})]) == ["INV-002: approved decision DEC-001 has no rationale (decisions/DEC-001.yaml)"]


def test_requirement_approval_contract():
    assert errors([artifact("REQ", "requirements/REQ-001.yaml", {"id": "REQ-001", "status": "APPROVED", "verification_method": ""})]) == ["INV-005: approved requirement REQ-001 has no verification_method (requirements/REQ-001.yaml)"]


def test_superseded_decision_requires_successor_contract():
    assert errors([artifact("DEC", "decisions/DEC-001.yaml", {"id": "DEC-001", "status": "SUPERSEDED", "superseded_by": None})]) == ["INV-003: superseded decision DEC-001 must declare superseded_by (decisions/DEC-001.yaml)"]


def test_superseded_requirement_rejects_wrong_kind_successor_contract():
    result = errors([
        artifact("REQ", "requirements/REQ-001.yaml", {"id": "REQ-001", "status": "SUPERSEDED", "superseded_by": "DEC-002"}),
        artifact("DEC", "decisions/DEC-002.yaml", {"id": "DEC-002", "status": "APPROVED", "rationale": "reason"}),
    ])
    assert result == ["INV-003: superseded requirement REQ-001 points to invalid successor 'DEC-002' (requirements/REQ-001.yaml)"]


def test_decision_supersedes_missing_predecessor_contract():
    assert errors([artifact("DEC", "decisions/DEC-002.yaml", {"id": "DEC-002", "status": "APPROVED", "rationale": "reason", "supersedes": ["DEC-404"]})]) == ["INV-007: decision DEC-002 supersedes missing decision DEC-404 (decisions/DEC-002.yaml)"]


def test_decision_supersession_reciprocity_contract():
    result = errors([
        artifact("DEC", "decisions/DEC-001.yaml", {"id": "DEC-001", "status": "APPROVED", "rationale": "reason"}),
        artifact("DEC", "decisions/DEC-002.yaml", {"id": "DEC-002", "status": "APPROVED", "rationale": "reason", "supersedes": ["DEC-001"]}),
    ])
    assert result == ["INV-007: decision DEC-002 supersedes DEC-001, but reciprocal supersession is not recorded"]


def test_state_done_failed_contract():
    assert errors([artifact("STATE", "state/current.yaml", {"status": "ACTIVE", "tasks": [{"id": "TASK-001", "status": "DONE", "verification_status": "FAILED"}]})]) == ["INV-004: task TASK-001 is DONE with FAILED verification (state/current.yaml)"]


def test_secret_scanner_contract(tmp_path):
    fake_secret = "gh" + "p_" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456"
    (tmp_path / "sample.txt").write_text(fake_secret, encoding="utf-8")
    (tmp_path / "sample.bin").write_text(fake_secret, encoding="utf-8")
    findings = scan_obvious_secrets(tmp_path)
    assert [f"{finding.code}: {finding.message}" for finding in findings] == ["INV-008: possible secret in sample.txt"]


def test_extract_references_contract():
    value = {"text": "DEC-001 REQ-002 RISK-003 TASK-004", "nested": ["REQ-005", {"value": "DEC-006"}]}
    assert extract_persistent_reference_ids(value) == {"DEC-001", "REQ-002", "RISK-003", "REQ-005", "DEC-006"}
