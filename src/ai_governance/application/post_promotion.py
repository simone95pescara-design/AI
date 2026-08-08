"""Application use case for baseline post-promotion integrity checks."""

from __future__ import annotations

from collections.abc import Collection, Mapping
from dataclasses import dataclass
from typing import Any

from ai_governance.domain.findings import Finding


@dataclass(frozen=True, slots=True)
class BaselineDocumentRule:
    """Expected markers for one baseline-facing normative document."""

    path: str
    required: tuple[str, ...]
    forbidden: tuple[str, ...] = ()


BASELINE_DOCUMENT_RULES: tuple[BaselineDocumentRule, ...] = (
    BaselineDocumentRule(
        path="governance/transition-model.md",
        required=("# Transition Model V1 — APPROVED", "Status: APPROVED"),
        forbidden=("APPROVED_CANDIDATE", "becomes normative only after"),
    ),
    BaselineDocumentRule(
        path="governance/repository-engineering.md",
        required=("# Repository Engineering V1 — APPROVATO", "Stato: APPROVATO"),
        forbidden=("PROPOSTA", "Stato: PROPOSTO", "diventa normativo solo dopo"),
    ),
    BaselineDocumentRule(
        path="governance/product-metamodel-v2.md",
        required=("# Product Metamodel V2 — APPROVED", "Stato: APPROVED"),
        forbidden=("Stato: PROPOSTO",),
    ),
)


def validate_post_promotion(
    documents: Mapping[str, str],
    current_state: Mapping[str, Any],
    approved_decision_ids: Collection[str],
) -> list[Finding]:
    """Validate that promoted baseline-facing projections match approved state."""

    findings: list[Finding] = []

    for rule in BASELINE_DOCUMENT_RULES:
        content = documents.get(rule.path)
        if content is None:
            findings.append(
                Finding(
                    code="POST-001",
                    message=f"missing baseline-facing document: {rule.path}",
                    source=rule.path,
                )
            )
            continue

        header = "\n".join(content.splitlines()[:6])
        for marker in rule.required:
            if marker not in header:
                findings.append(
                    Finding(
                        code="POST-001",
                        message=f"missing approved baseline marker: {marker}",
                        source=rule.path,
                    )
                )
        for marker in rule.forbidden:
            if marker in header:
                findings.append(
                    Finding(
                        code="POST-001",
                        message=f"stale candidate/proposal marker remains: {marker}",
                        source=rule.path,
                    )
                )

    baseline = str(current_state.get("baseline", ""))
    for decision_id in sorted(approved_decision_ids):
        if decision_id not in baseline:
            findings.append(
                Finding(
                    code="POST-002",
                    message=f"approved decision missing from state baseline projection: {decision_id}",
                    source="state/current.yaml",
                    location="baseline",
                )
            )

    return findings
