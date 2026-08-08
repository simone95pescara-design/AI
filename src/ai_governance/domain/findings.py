"""Core validation/compliance finding domain model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class Finding:
    """One structured validation, compliance or diagnostic finding."""

    code: str
    message: str
    severity: str = "ERROR"
    source: str | None = None
    location: str | None = None
    rule: str | None = None
    context: Mapping[str, Any] | None = None
