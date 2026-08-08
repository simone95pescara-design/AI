"""Repository security scanning primitives."""

from __future__ import annotations

import re
from pathlib import Path

from ai_governance.domain.findings import Finding

_TEXT_SUFFIXES = frozenset({".md", ".py", ".json", ".yaml", ".yml", ".txt"})
_SECRET_PATTERNS = (
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)


def scan_obvious_secrets(repository_root: Path) -> list[Finding]:
    """Return INV-008 findings for obvious secret patterns in repository text files."""

    findings: list[Finding] = []
    for path in repository_root.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() not in _TEXT_SUFFIXES:
            continue

        text = path.read_text(encoding="utf-8", errors="ignore")
        if any(pattern.search(text) for pattern in _SECRET_PATTERNS):
            source = str(path.relative_to(repository_root))
            findings.append(
                Finding(
                    code="INV-008",
                    message=f"possible secret in {source}",
                    source=source,
                )
            )
    return findings
