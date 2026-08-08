from pathlib import Path

from ai_governance.infrastructure.artifact_repository import (
    discover_artifact_paths,
    load_artifact_documents,
)


def test_discovery_is_deterministic_and_filters_suffixes(tmp_path: Path) -> None:
    decisions = tmp_path / "decisions"
    decisions.mkdir()
    (decisions / "B.yaml").write_text("id: DEC-002\n", encoding="utf-8")
    (decisions / "A.json").write_text('{"id": "DEC-001"}', encoding="utf-8")
    (decisions / "ignore.md").write_text("ignored", encoding="utf-8")

    discovered = discover_artifact_paths(
        {"DEC": decisions},
        frozenset({".yaml", ".yml", ".json"}),
    )

    assert discovered == [
        ("DEC", decisions / "A.json"),
        ("DEC", decisions / "B.yaml"),
    ]


def test_loading_preserves_kind_path_and_parsed_data(tmp_path: Path) -> None:
    requirements = tmp_path / "requirements"
    requirements.mkdir()
    path = requirements / "REQ-001.yaml"
    path.write_text("id: REQ-001\nstatus: APPROVED\n", encoding="utf-8")

    loaded, issues = load_artifact_documents(
        {"REQ": requirements},
        frozenset({".yaml", ".yml", ".json"}),
    )

    assert issues == []
    assert len(loaded) == 1
    assert loaded[0].kind == "REQ"
    assert loaded[0].path == path
    assert loaded[0].data == {"id": "REQ-001", "status": "APPROVED"}


def test_parse_failure_is_returned_as_issue_without_hiding_document(tmp_path: Path) -> None:
    risks = tmp_path / "risks"
    risks.mkdir()
    path = risks / "RISK-001.json"
    path.write_text("{invalid", encoding="utf-8")

    loaded, issues = load_artifact_documents(
        {"RISK": risks},
        frozenset({".yaml", ".yml", ".json"}),
    )

    assert loaded == []
    assert len(issues) == 1
    assert issues[0].kind == "RISK"
    assert issues[0].path == path
    assert isinstance(issues[0].error, Exception)
