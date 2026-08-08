from ai_governance.application.repository_compliance import (
    RepositoryComplianceSnapshot,
    SchemaContract,
    evaluate_repository_compliance,
)
from ai_governance.domain.artifacts import Artifact
from ai_governance.domain.findings import Finding


def test_application_aggregates_structural_semantic_and_security_findings():
    snapshot = RepositoryComplianceSnapshot(
        artifacts=(
            Artifact(
                kind="DEC",
                data={"id": "DEC-001", "status": "APPROVED", "rationale": ""},
                source="decisions/DEC-001.yaml",
            ),
        ),
        schemas={
            "DEC": SchemaContract(
                data={
                    "$schema": "https://json-schema.org/draft/2020-12/schema",
                    "type": "object",
                    "required": ["id", "status", "rationale"],
                    "properties": {
                        "id": {"type": "string"},
                        "status": {"type": "string"},
                        "rationale": {"type": "string"},
                    },
                },
                source="schemas/decision.schema.json",
            )
        },
        preflight_findings=(Finding(code="CHECK-001", message="preflight"),),
        security_findings=(Finding(code="INV-008", message="security"),),
    )

    findings = evaluate_repository_compliance(snapshot)
    codes = [finding.code for finding in findings]

    assert codes[0] == "CHECK-001"
    assert "INV-002" in codes
    assert codes[-1] == "INV-008"


def test_invalid_schema_reports_structured_source_and_rule():
    snapshot = RepositoryComplianceSnapshot(
        artifacts=(),
        schemas={
            "REQ": SchemaContract(
                data={"type": "array"},
                source="schemas/requirement.schema.json",
            )
        },
    )

    findings = evaluate_repository_compliance(snapshot)

    assert len(findings) == 1
    assert findings[0].code == "CHECK-002"
    assert findings[0].source == "schemas/requirement.schema.json"
    assert findings[0].rule == "schema-definition"
