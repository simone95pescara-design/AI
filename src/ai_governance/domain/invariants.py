"""Pure domain invariants over governance artifacts."""

from __future__ import annotations

from collections.abc import Iterable

from ai_governance.domain.artifacts import Artifact
from ai_governance.domain.findings import Finding


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
