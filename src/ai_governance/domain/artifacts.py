"""Core artifact domain model.

The domain model is intentionally independent from filesystem, serialization and
repository implementations. Infrastructure adapters translate their physical
representations into these types at architectural boundaries.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Artifact:
    """One structured governance artifact presented to application/domain logic."""

    kind: str
    data: dict[str, Any]
    source: str | None = None

    @property
    def artifact_id(self) -> str | None:
        """Return the persistent artifact ID when the document exposes one."""

        value = self.data.get("id")
        return value if isinstance(value, str) else None
