from __future__ import annotations

import re
from pathlib import Path

from ai_governance.infrastructure.repository_registry import REQUIRED_PATHS

REPO = Path(__file__).resolve().parents[2]

KEBAB_MD = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
SNAKE_PY = re.compile(r"^[a-z][a-z0-9_]*\.py$")
SCHEMA_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.schema\.json$")
TEMPLATE_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.yaml$")
TOP_LEVEL_DIR = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

EXPECTED_REQUIRED_PATHS = {
    Path("README.md"),
    Path("AGENTS.md"),
    Path("BOOTSTRAP.md"),
    Path("pyproject.toml"),
    Path("governance/specification.md"),
    Path("governance/authority.md"),
    Path("governance/knowledge-policy.md"),
    Path("governance/response-protocol.md"),
    Path("governance/invariants.md"),
    Path("governance/transition-model.md"),
    Path("governance/repository-engineering.md"),
    Path("governance/product-metamodel-v2.md"),
    Path("state/current.yaml"),
}

LEGACY_OPERATIONAL_PATHS = (
    "compliance/validate.py",
    "compliance/requirements.txt",
    "governance/SPECIFICATION.md",
)


def test_application_python_is_owned_by_src() -> None:
    violations = []
    for path in REPO.rglob("*.py"):
        relative = path.relative_to(REPO)
        if relative.parts[0] not in {"src", "tests"}:
            violations.append(str(relative))
    assert violations == []


def test_only_root_readme_is_allowed() -> None:
    readmes = sorted(path.relative_to(REPO) for path in REPO.rglob("README.md"))
    assert readmes == [Path("README.md")]


def test_repository_top_level_directory_names_are_deterministic() -> None:
    violations = []
    for path in REPO.iterdir():
        if not path.is_dir() or path.name == ".git":
            continue
        if path.name == ".github":
            continue
        if not TOP_LEVEL_DIR.fullmatch(path.name):
            violations.append(path.name)
    assert violations == []


def test_human_document_names_follow_policy() -> None:
    violations = []
    for owner in (REPO / "governance", REPO / "docs"):
        for path in owner.glob("*.md"):
            if not KEBAB_MD.fullmatch(path.name):
                violations.append(str(path.relative_to(REPO)))
    assert violations == []


def test_schema_template_and_persistent_artifact_names_follow_policy() -> None:
    violations = []

    for path in (REPO / "schemas").glob("*.schema.json"):
        if not SCHEMA_NAME.fullmatch(path.name):
            violations.append(str(path.relative_to(REPO)))

    for path in (REPO / "templates").glob("*.yaml"):
        if not TEMPLATE_NAME.fullmatch(path.name):
            violations.append(str(path.relative_to(REPO)))

    artifact_patterns = {
        "decisions": re.compile(r"^DEC-\d{3}\.yaml$"),
        "requirements": re.compile(r"^REQ-\d{3}\.yaml$"),
        "risks": re.compile(r"^RISK-\d{3}\.yaml$"),
    }
    for directory, pattern in artifact_patterns.items():
        for path in (REPO / directory).glob("*.yaml"):
            if not pattern.fullmatch(path.name):
                violations.append(str(path.relative_to(REPO)))

    assert violations == []


def test_python_module_and_test_names_follow_policy() -> None:
    violations = []
    for path in (REPO / "src" / "ai_governance").rglob("*.py"):
        if path.name == "__init__.py":
            continue
        if not SNAKE_PY.fullmatch(path.name):
            violations.append(str(path.relative_to(REPO)))

    for path in (REPO / "tests").rglob("*.py"):
        if path.name == "conftest.py":
            continue
        if not path.name.startswith("test_") or not SNAKE_PY.fullmatch(path.name):
            violations.append(str(path.relative_to(REPO)))

    assert violations == []


def test_required_bootstrap_and_normative_paths_are_explicit_and_present() -> None:
    assert set(REQUIRED_PATHS) == EXPECTED_REQUIRED_PATHS
    missing = sorted(str(path) for path in REQUIRED_PATHS if not (REPO / path).is_file())
    assert missing == []


def test_pyproject_is_only_python_dependency_source() -> None:
    competing = []
    for path in REPO.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        name = path.name
        if name in {"setup.py", "setup.cfg", "Pipfile"} or (
            name.startswith("requirements") and name.endswith(".txt")
        ):
            competing.append(str(path.relative_to(REPO)))
    assert competing == []


def test_legacy_operational_paths_do_not_reappear() -> None:
    for legacy in LEGACY_OPERATIONAL_PATHS:
        assert not (REPO / legacy).exists(), legacy

    operational_files = [
        REPO / "README.md",
        REPO / "AGENTS.md",
        REPO / "BOOTSTRAP.md",
        REPO / "state" / "current.yaml",
        *sorted((REPO / ".github" / "workflows").glob("*.yml")),
        *sorted((REPO / ".github" / "workflows").glob("*.yaml")),
        *sorted((REPO / "src").rglob("*.py")),
    ]
    violations = []
    for path in operational_files:
        text = path.read_text(encoding="utf-8")
        for legacy in LEGACY_OPERATIONAL_PATHS:
            if legacy in text:
                violations.append(f"{path.relative_to(REPO)} -> {legacy}")
    assert violations == []
