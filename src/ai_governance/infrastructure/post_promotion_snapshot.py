"""Filesystem adapter for post-promotion baseline integrity checks."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from ai_governance.application.post_promotion import BASELINE_DOCUMENT_RULES


def load_post_promotion_snapshot(
    repository_root: Path,
) -> tuple[dict[str, str], dict[str, Any], set[str]]:
    """Load baseline-facing documents, current state and approved decision IDs."""

    documents = {
        rule.path: (repository_root / rule.path).read_text(encoding="utf-8")
        for rule in BASELINE_DOCUMENT_RULES
        if (repository_root / rule.path).is_file()
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
