from ai_governance.application.post_promotion import validate_post_promotion


def valid_documents() -> dict[str, str]:
    return {
        "governance/transition-model.md": "# Transition Model V1 — APPROVED\nStatus: APPROVED\n",
        "governance/repository-engineering.md": "# Repository Engineering V1 — APPROVATO\nStato: APPROVATO\n",
        "governance/product-metamodel-v2.md": "# Product Metamodel V2 — APPROVED\nStato: APPROVED\n",
    }


def test_post_promotion_accepts_consistent_baseline_markers_and_state():
    findings = validate_post_promotion(
        valid_documents(),
        {"baseline": "Governance / DEC-001 + DEC-002 + DEC-004 + DEC-005"},
        {"DEC-001", "DEC-002", "DEC-004", "DEC-005"},
    )

    assert findings == []


def test_post_promotion_rejects_candidate_marker_on_promoted_document():
    documents = valid_documents()
    documents["governance/transition-model.md"] = (
        "# Transition Model V1 — APPROVED CANDIDATE\nStatus: APPROVED_CANDIDATE\n"
    )

    findings = validate_post_promotion(
        documents,
        {"baseline": "DEC-001"},
        {"DEC-001"},
    )

    assert any(finding.code == "POST-001" for finding in findings)


def test_post_promotion_rejects_approved_decision_missing_from_state_projection():
    findings = validate_post_promotion(
        valid_documents(),
        {"baseline": "DEC-001 + DEC-002 + DEC-004"},
        {"DEC-001", "DEC-002", "DEC-004", "DEC-005"},
    )

    assert any(
        finding.code == "POST-002" and "DEC-005" in finding.message
        for finding in findings
    )
