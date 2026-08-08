from pathlib import Path

from ai_governance.application.post_promotion import (
    BASELINE_DOCUMENT_RULES,
    validate_post_promotion,
)
from ai_governance.infrastructure.post_promotion_snapshot import (
    load_post_promotion_snapshot,
)


REPO = Path(__file__).resolve().parents[2]


def test_current_baseline_passes_post_promotion_integrity():
    document_paths = tuple(rule.path for rule in BASELINE_DOCUMENT_RULES)
    documents, current_state, approved_decision_ids = load_post_promotion_snapshot(
        REPO, document_paths
    )

    assert validate_post_promotion(
        documents, current_state, approved_decision_ids
    ) == []
