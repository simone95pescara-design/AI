"""Core persistent-reference domain model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Reference:
    """A persistent relationship from one artifact/context to another artifact ID."""

    target_id: str
    expected_kind: str | None = None
    source_id: str | None = None
    field: str | None = None
