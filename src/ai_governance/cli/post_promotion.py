"""CLI entry module for post-promotion integrity verification."""

from __future__ import annotations

from pathlib import Path

from ai_governance.application.post_promotion import (
    BASELINE_DOCUMENT_RULES,
    validate_post_promotion,
)
from ai_governance.infrastructure.post_promotion_snapshot import (
    load_post_promotion_snapshot,
)


def main(repository_root: Path | None = None) -> int:
    root = (repository_root or Path.cwd()).resolve()
    document_paths = tuple(rule.path for rule in BASELINE_DOCUMENT_RULES)
    documents, current_state, approved_decision_ids = load_post_promotion_snapshot(
        root, document_paths
    )
    findings = validate_post_promotion(
        documents, current_state, approved_decision_ids
    )

    if findings:
        print("POST-PROMOTION: FAIL")
        for finding in findings:
            source = f" [{finding.source}]" if finding.source else ""
            print(f"- {finding.code}{source}: {finding.message}")
        return 1

    print("POST-PROMOTION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
