"""Core validation/compliance finding domain model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Finding:
    """One structured validation, compliance or diagnostic finding."""

    code: str
    message: str
    source: str | None = None
    location: str | None = None
