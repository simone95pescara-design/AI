from __future__ import annotations

import ast
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = REPO / "src" / "ai_governance"
LAYERS = {"domain", "application", "infrastructure", "cli"}

FORBIDDEN_LAYER_IMPORTS = {
    "domain": {"application", "infrastructure", "cli"},
    "application": {"infrastructure", "cli"},
    "infrastructure": {"cli"},
    "cli": {"domain"},
}


def source_layer(path: Path) -> str | None:
    relative = path.relative_to(PACKAGE_ROOT)
    return relative.parts[0] if relative.parts and relative.parts[0] in LAYERS else None


def absolute_target(node: ast.ImportFrom, path: Path) -> str | None:
    if node.level == 0:
        return node.module

    relative_parent = path.parent.relative_to(PACKAGE_ROOT)
    package_parts = ["ai_governance", *relative_parent.parts]
    keep = len(package_parts) - (node.level - 1)
    if keep < 1:
        return None
    target_parts = package_parts[:keep]
    if node.module:
        target_parts.extend(node.module.split("."))
    return ".".join(target_parts)


def imported_internal_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    targets: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            targets.update(alias.name for alias in node.names if alias.name.startswith("ai_governance"))
        elif isinstance(node, ast.ImportFrom):
            target = absolute_target(node, path)
            if target and target.startswith("ai_governance"):
                targets.add(target)
    return targets


def target_layer(module: str) -> str | None:
    parts = module.split(".")
    if len(parts) >= 2 and parts[0] == "ai_governance" and parts[1] in LAYERS:
        return parts[1]
    return None


def test_expected_package_layers_exist():
    assert PACKAGE_ROOT.is_dir()
    assert {path.name for path in PACKAGE_ROOT.iterdir() if path.is_dir()} == LAYERS
    for layer in LAYERS:
        assert (PACKAGE_ROOT / layer / "__init__.py").is_file()


def test_package_root_does_not_accumulate_unowned_modules():
    root_python_files = {path.name for path in PACKAGE_ROOT.glob("*.py")}
    assert root_python_files == {"__init__.py"}


def test_layer_import_direction():
    violations: list[str] = []
    for path in sorted(PACKAGE_ROOT.rglob("*.py")):
        layer = source_layer(path)
        if layer is None:
            continue
        forbidden = FORBIDDEN_LAYER_IMPORTS[layer]
        for module in imported_internal_modules(path):
            imported_layer = target_layer(module)
            if imported_layer in forbidden:
                violations.append(
                    f"{path.relative_to(REPO)}: {layer} must not import {module}"
                )
    assert violations == []
