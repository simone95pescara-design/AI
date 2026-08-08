import importlib.util
from pathlib import Path

from ai_governance.infrastructure.repository_registry import (
    SUPPORTED_DOCUMENT_SUFFIXES,
    artifact_roots,
    required_paths,
    schema_paths,
)


REPO = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = REPO / "compliance" / "validate.py"


def load_legacy_validator():
    spec = importlib.util.spec_from_file_location("legacy_validate_registry_test", VALIDATOR_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_legacy_layout_constants_are_registry_projections() -> None:
    validator = load_legacy_validator()

    assert validator.REQUIRED == required_paths(validator.REPO)
    assert validator.SCHEMAS == schema_paths(validator.REPO)
    assert validator.ARTIFACT_ROOTS == artifact_roots(validator.REPO)
    assert validator.SUPPORTED_SUFFIXES == SUPPORTED_DOCUMENT_SUFFIXES
