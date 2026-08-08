from __future__ import annotations

import re
import subprocess
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


def tracked_paths(pattern: str | None = None) -> list[Path]:
    command = ["git", "ls-files"]
    if pattern is not None:
        command.extend(["--", pattern])
    result = subprocess.run(
        command,
        cwd=REPO,
        check=True,
        capture_output=True,
        text=True,
    )
    return [Path(line) for line in result.stdout.splitlines() if line]


def test_application_python_is_owned_by_src() -> None:
    violations = []
    for relative in tracked_paths("*.py"):
        if relative.parts[0] not in {"src", "tests"}:
            violations.append(str(relative))
    assert violations == []


def test_only_root_readme_is_allowed() -> None:
    readmes = sorted(path for path in tracked_paths() if path.name == "README.md")
    assert readmes == [Path("README.md")]


def test_repository_top_level_directory_names_are_deterministic() -> None:
    top_level_dirs = {path.parts[0] for path in tracked_paths() if len(path.parts) > 1}
    violations = []
    for name in sorted(top_level_dirs):
        if name == ".github":
            continue
        if not TOP_LEVEL_DIR.fullmatch(name):
            violations.append(name)
    assert violations == []


def test_human_document_names_follow_policy() -> None:
    violations = []
    for relative in tracked_paths():
        if len(relative.parts) != 2 or relative.parts[0] not in {"governance", "docs"}:
            continue
        if relative.suffix == ".md" and not KEBAB_MD.fullmatch(relative.name):
            violations.append(str(relative))
    assert violations == []


def test_schema_template_and_persistent_artifact_names_follow_policy() -> None:
    violations = []

    for relative in tracked_paths():
        if len(relative.parts) != 2:
            continue
        directory = relative.parts[0]
        if directory == "schemas" and relative.name.endswith(".schema.json"):
            if not SCHEMA_NAME.fullmatch(relative.name):
                violations.append(str(relative))
        elif directory == "templates" and relative.suffix == ".yaml":
            if not TEMPLATE_NAME.fullmatch(relative.name):
                violations.append(str(relative))

    artifact_patterns = {
        "decisions": re.compile(r"^DEC-\d{3}\.yaml$"),
        "requirements": re.compile(r"^REQ-\d{3}\.yaml$"),
        "risks": re.compile(r"^RISK-\d{3}\.yaml$"),
    }
    for relative in tracked_paths():
        if len(relative.parts) != 2:
            continue
        pattern = artifact_patterns.get(relative.parts[0])
        if pattern and relative.suffix == ".yaml" and not pattern.fullmatch(relative.name):
            violations.append(str(relative))

    assert violations == []


def test_python_module_and_test_names_follow_policy() -> None:
    violations = []
    for relative in tracked_paths("*.py"):
        if relative.parts[0] == "src":
            if relative.name == "__init__.py":
                continue
            if not SNAKE_PY.fullmatch(relative.name):
                violations.append(str(relative))
        elif relative.parts[0] == "tests":
            if relative.name == "conftest.py":
                continue
            if not relative.name.startswith("test_") or not SNAKE_PY.fullmatch(relative.name):
                violations.append(str(relative))

    assert violations == []


def test_required_bootstrap_and_normative_paths_are_explicit_and_present() -> None:
    assert set(REQUIRED_PATHS) == EXPECTED_REQUIRED_PATHS
    missing = sorted(str(path) for path in REQUIRED_PATHS if not (REPO / path).is_file())
    assert missing == []


def test_pyproject_is_only_python_dependency_source() -> None:
    competing = []
    for relative in tracked_paths():
        name = relative.name
        if name in {"setup.py", "setup.cfg", "Pipfile"} or (
            name.startswith("requirements") and name.endswith(".txt")
        ):
            competing.append(str(relative))
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
