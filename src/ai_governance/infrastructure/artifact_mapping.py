"""Adapters from physical repository documents to domain artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ai_governance.domain.artifacts import Artifact


def domain_artifact(
    *,
    kind: str,
    path: Path,
    data: dict[str, Any],
    repository_root: Path,
) -> Artifact:
    """Translate one parsed repository object into a filesystem-independent Artifact."""

    try:
        source = path.relative_to(repository_root).as_posix()
    except ValueError:
        source = path.as_posix()
    return Artifact(kind=kind, data=data, source=source)
