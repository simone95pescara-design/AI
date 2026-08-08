from pathlib import Path

from ai_governance.infrastructure.repository_registry import (
    ARTIFACT_TYPES,
    REQUIRED_PATHS,
    SUPPORTED_DOCUMENT_SUFFIXES,
    artifact_roots,
    required_paths,
    schema_paths,
)


def test_registry_has_unique_relative_paths() -> None:
    roots = [config.root for config in ARTIFACT_TYPES.values()]
    schemas = [config.schema for config in ARTIFACT_TYPES.values()]

    assert all(not path.is_absolute() for path in REQUIRED_PATHS)
    assert all(not path.is_absolute() for path in roots)
    assert all(not path.is_absolute() for path in schemas)
    assert len(roots) == len(set(roots))
    assert len(schemas) == len(set(schemas))


def test_registry_resolves_current_baseline_layout(tmp_path: Path) -> None:
    assert required_paths(tmp_path) == tuple(tmp_path / path for path in REQUIRED_PATHS)
    assert set(artifact_roots(tmp_path)) == set(ARTIFACT_TYPES)
    assert set(schema_paths(tmp_path)) == set(ARTIFACT_TYPES)

    for kind, config in ARTIFACT_TYPES.items():
        assert artifact_roots(tmp_path)[kind] == tmp_path / config.root
        assert schema_paths(tmp_path)[kind] == tmp_path / config.schema


def test_supported_document_suffixes_are_explicit() -> None:
    assert SUPPORTED_DOCUMENT_SUFFIXES == {".yaml", ".yml", ".json"}
