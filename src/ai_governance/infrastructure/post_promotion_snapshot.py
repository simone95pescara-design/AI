"""Filesystem adapter for post-promotion baseline integrity checks."""

from __future__ import annotations

from collections.abc import Collection
from pathlib import Path
from typing import Any

import yaml


def load_post_promotion_snapshot(
    repository_root: Path,
    document_paths: Collection[str],
) -> tuple[dict[str, str], dict[str, Any], set[str]]:
    """Load baseline-facing documents, current state and approved decision IDs."""

    documents = {
        path: (repository_root / path).read_text(encoding="utf-8")
        for path in document_paths
        if (repository_root / path).is_file()
    }

    state_path = repository_root / "state" / "current.yaml"
    state_data = yaml.safe_load(state_path.read_text(encoding="utf-8"))
    current_state = state_data if isinstance(state_data, dict) else {}

    approved_decision_ids: set[str] = set()
    for path in sorted((repository_root / "decisions").glob("DEC-*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and data.get("status") == "APPROVED":
            decision_id = data.get("id")
            if isinstance(decision_id, str):
                approved_decision_ids.add(decision_id)

    return documents, current_state, approved_decision_ids
