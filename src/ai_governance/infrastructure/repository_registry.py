"""Technical repository layout registry.

This module translates the currently active governance metamodel into filesystem
configuration. It does not define or activate governance concepts by itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ArtifactTypeConfig:
    """Filesystem configuration for one active artifact type."""

    kind: str
    root: Path
    schema: Path


REQUIRED_PATHS: tuple[Path, ...] = (
    Path("AGENTS.md"),
    Path("governance/SPECIFICATION.md"),
    Path("governance/authority.md"),
    Path("governance/knowledge-policy.md"),
    Path("governance/response-protocol.md"),
    Path("governance/invariants.md"),
)

ARTIFACT_TYPES: dict[str, ArtifactTypeConfig] = {
    "DEC": ArtifactTypeConfig("DEC", Path("decisions"), Path("schemas/decision.schema.json")),
    "REQ": ArtifactTypeConfig("REQ", Path("requirements"), Path("schemas/requirement.schema.json")),
    "RISK": ArtifactTypeConfig("RISK", Path("risks"), Path("schemas/risk.schema.json")),
    "STATE": ArtifactTypeConfig("STATE", Path("state"), Path("schemas/state.schema.json")),
}

SUPPORTED_DOCUMENT_SUFFIXES = frozenset({".yaml", ".yml", ".json"})


def required_paths(repository_root: Path) -> tuple[Path, ...]:
    """Return absolute required paths for a repository root."""

    return tuple(repository_root / path for path in REQUIRED_PATHS)


def artifact_roots(repository_root: Path) -> dict[str, Path]:
    """Return absolute owner roots keyed by artifact kind."""

    return {
        kind: repository_root / config.root
        for kind, config in ARTIFACT_TYPES.items()
    }


def schema_paths(repository_root: Path) -> dict[str, Path]:
    """Return absolute schema paths keyed by artifact kind."""

    return {
        kind: repository_root / config.schema
        for kind, config in ARTIFACT_TYPES.items()
    }
