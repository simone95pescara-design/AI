"""Repository adapter for artifact discovery and document loading.

This module owns filesystem traversal and parsing only. Schema and semantic
validation remain outside this adapter so infrastructure does not decide
normative validity.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from ai_governance.infrastructure.document_io import load_document


@dataclass(frozen=True, slots=True)
class LoadedArtifact:
    """One successfully parsed artifact document."""

    kind: str
    path: Path
    data: Any


@dataclass(frozen=True, slots=True)
class ArtifactLoadIssue:
    """A document that was discovered but could not be parsed."""

    kind: str
    path: Path
    error: Exception


def discover_artifact_paths(
    artifact_roots: Mapping[str, Path],
    supported_suffixes: frozenset[str] | set[str],
) -> list[tuple[str, Path]]:
    """Discover supported artifact files in deterministic order."""

    discovered: list[tuple[str, Path]] = []
    for kind, root in artifact_roots.items():
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if path.is_file() and path.suffix.lower() in supported_suffixes:
                discovered.append((kind, path))
    return discovered


def load_artifact_documents(
    artifact_roots: Mapping[str, Path],
    supported_suffixes: frozenset[str] | set[str],
) -> tuple[list[LoadedArtifact], list[ArtifactLoadIssue]]:
    """Discover and parse artifact documents without validating their schema."""

    loaded: list[LoadedArtifact] = []
    issues: list[ArtifactLoadIssue] = []

    for kind, path in discover_artifact_paths(artifact_roots, supported_suffixes):
        try:
            data = load_document(path)
        except Exception as exc:  # preserve parser exception for legacy formatting
            issues.append(ArtifactLoadIssue(kind=kind, path=path, error=exc))
            continue
        loaded.append(LoadedArtifact(kind=kind, path=path, data=data))

    return loaded, issues
