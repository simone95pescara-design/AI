"""Thin command-line entry point for repository governance compliance."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ai_governance.application.repository_compliance import evaluate_repository_compliance
from ai_governance.infrastructure.repository_compliance_snapshot import (
    load_repository_compliance_snapshot,
)

PASS_LINES = (
    "CHECK-001 required governance files present",
    "CHECK-002 schemas valid JSON Schema",
    "CHECK-003 artifact files match their schemas",
    "INV-001 requirement references resolve",
    "INV-002 approved decisions have rationale",
    "INV-003 superseded artifacts identify valid successors",
    "INV-004 DONE tasks are not verification FAILED",
    "INV-005 approved requirements have verification methods",
    "INV-006 persistent IDs are unique",
    "INV-007 decision supersession is reciprocal",
    "INV-008 no obvious secrets detected",
)


def render_finding(finding: Any) -> str:
    """Render one structured finding without changing its semantics."""

    if finding.code == "CHECK-003" and finding.source and finding.location:
        return f"{finding.code}: {finding.source} [{finding.location}]: {finding.message}"
    return f"{finding.code}: {finding.message}"


def main(repository_root: Path | None = None) -> int:
    root = (repository_root or Path.cwd()).resolve()
    snapshot = load_repository_compliance_snapshot(root)
    findings = evaluate_repository_compliance(snapshot)

    if findings:
        print("COMPLIANCE: FAIL")
        for finding in findings:
            print(f"- {render_finding(finding)}")
        return 1

    print("COMPLIANCE: PASS")
    for line in PASS_LINES:
        print(f"- {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
