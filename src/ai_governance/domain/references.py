"""Core persistent-reference domain model and parsing."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

PERSISTENT_ID_PATTERN = re.compile(r"\b(?:DEC|REQ|RISK)-\d{3,}\b")


@dataclass(frozen=True, slots=True)
class Reference:
    """A persistent relationship from one artifact/context to another artifact ID."""

    target_id: str
    expected_kind: str | None = None
    source_id: str | None = None
    field: str | None = None


def extract_persistent_reference_ids(value: Any) -> set[str]:
    """Extract legacy persistent IDs recursively from strings, lists and mappings."""

    refs: set[str] = set()
    if isinstance(value, str):
        refs.update(PERSISTENT_ID_PATTERN.findall(value))
    elif isinstance(value, list):
        for item in value:
            refs.update(extract_persistent_reference_ids(item))
    elif isinstance(value, dict):
        for item in value.values():
            refs.update(extract_persistent_reference_ids(item))
    return refs
