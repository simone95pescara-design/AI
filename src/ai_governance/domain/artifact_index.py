"""Domain lookup for persistent governance artifacts."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from ai_governance.domain.artifacts import Artifact


@dataclass(frozen=True, slots=True)
class ArtifactIndex:
    """Lookup persistent artifacts by ID without infrastructure concerns.

    STATE artifacts are projections and are intentionally excluded. If duplicate
    IDs are present, the last artifact wins to preserve the legacy semantic
    lookup behavior; INV-006 reports the duplication separately.
    """

    by_id: dict[str, Artifact]

    @classmethod
    def from_artifacts(cls, artifacts: Iterable[Artifact]) -> "ArtifactIndex":
        indexed: dict[str, Artifact] = {}
        for artifact in artifacts:
            if artifact.kind == "STATE":
                continue
            item_id = artifact.artifact_id
            if item_id is not None:
                indexed[item_id] = artifact
        return cls(by_id=indexed)

    def get(self, artifact_id: str) -> Artifact | None:
        return self.by_id.get(artifact_id)
