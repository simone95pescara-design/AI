"""Filesystem document loading for machine-readable governance artifacts.

This module owns serialization concerns only. It does not know artifact semantics,
invariants, repository policy, or CLI behavior.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


def load_json_schema(path: Path) -> dict[str, Any]:
    """Load a JSON schema from *path* preserving the legacy decoding behavior."""
    return json.loads(path.read_text(encoding="utf-8"))


def load_document(path: Path) -> Any:
    """Load JSON by suffix and YAML otherwise, preserving legacy behavior."""
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    return yaml.safe_load(text)
