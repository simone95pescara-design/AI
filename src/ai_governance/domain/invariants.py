"""Pure domain invariants over governance artifacts."""

from __future__ import annotations

from collections.abc import Iterable

from ai_governance.domain.artifacts import Artifact
from ai_governance.domain.findings import Finding


def _nonempty_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def find_approved_decisions_without_rationale(
    artifacts: Iterable[Artifact],
) -> list[Finding]:
    """Return INV-002 findings for approved decisions without rationale."""

    findings: list[Finding] = []
    for artifact in artifacts:
        if artifact.kind != "DEC" or artifact.data.get("status") != "APPROVED":
            continue
        if _nonempty_text(artifact.data.get("rationale")):
            continue

        source = artifact.source or "<unknown>"
        item_id = artifact.artifact_id or source
        findings.append(
            Finding(
                code="INV-002",
                message=f"approved decision {item_id} has no rationale ({source})",
                source=source,
                location="rationale",
            )
        )
    return findings


def find_duplicate_ids(artifacts: Iterable[Artifact]) -> list[Finding]:
    """Return INV-006 findings for duplicate persistent IDs.

    STATE artifacts are projections and therefore do not participate in the
    persistent-ID uniqueness invariant.
    """

    seen: dict[str, str | None] = {}
    findings: list[Finding] = []

    for artifact in artifacts:
        if artifact.kind == "STATE":
            continue

        item_id = artifact.artifact_id
        if item_id is None:
            continue

        if item_id in seen and seen[item_id] != artifact.source:
            first_source = seen[item_id] or "<unknown>"
            second_source = artifact.source or "<unknown>"
            findings.append(
                Finding(
                    code="INV-006",
                    message=f"duplicate ID {item_id}: {first_source} and {second_source}",
                    source=second_source,
                )
            )
        else:
            seen[item_id] = artifact.source

    return findings
