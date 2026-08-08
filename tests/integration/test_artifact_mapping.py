from pathlib import Path

from ai_governance.infrastructure.artifact_mapping import domain_artifact


def test_domain_artifact_uses_repository_relative_logical_source(tmp_path: Path) -> None:
    path = tmp_path / "requirements" / "REQ-001.yaml"
    artifact = domain_artifact(
        kind="REQ",
        path=path,
        data={"id": "REQ-001", "status": "APPROVED"},
        repository_root=tmp_path,
    )

    assert artifact.kind == "REQ"
    assert artifact.artifact_id == "REQ-001"
    assert artifact.source == "requirements/REQ-001.yaml"
    assert artifact.data["status"] == "APPROVED"


def test_domain_artifact_preserves_external_source_when_not_under_root(tmp_path: Path) -> None:
    repository_root = tmp_path / "repo"
    external = tmp_path / "external" / "REQ-001.yaml"
    artifact = domain_artifact(
        kind="REQ",
        path=external,
        data={"id": "REQ-001"},
        repository_root=repository_root,
    )

    assert artifact.source == external.as_posix()
