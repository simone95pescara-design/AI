from ai_governance.domain.artifacts import Artifact
from ai_governance.domain.invariants import find_done_tasks_with_failed_verification


def test_done_task_with_failed_verification_is_reported() -> None:
    state = Artifact(
        kind="STATE",
        data={
            "tasks": [
                {
                    "id": "TASK-001",
                    "status": "DONE",
                    "verification_status": "FAILED",
                }
            ]
        },
        source="state/current.yaml",
    )

    findings = find_done_tasks_with_failed_verification([state])

    assert len(findings) == 1
    assert findings[0].code == "INV-004"
    assert findings[0].message == (
        "task TASK-001 is DONE with FAILED verification (state/current.yaml)"
    )
    assert findings[0].source == "state/current.yaml"
    assert findings[0].location == "tasks"


def test_non_state_or_non_failed_done_tasks_do_not_trigger_inv_004() -> None:
    artifacts = [
        Artifact(
            kind="STATE",
            data={"tasks": [{"id": "TASK-001", "status": "IN_PROGRESS", "verification_status": "FAILED"}]},
            source="state/current.yaml",
        ),
        Artifact(
            kind="STATE",
            data={"tasks": [{"id": "TASK-002", "status": "DONE", "verification_status": "PASSED"}]},
            source="state/current.yaml",
        ),
        Artifact(
            kind="REQ",
            data={"tasks": [{"id": "TASK-003", "status": "DONE", "verification_status": "FAILED"}]},
            source="requirements/REQ-001.yaml",
        ),
    ]

    assert find_done_tasks_with_failed_verification(artifacts) == []


def test_inv_004_preserves_legacy_unknown_task_id_message() -> None:
    state = Artifact(
        kind="STATE",
        data={"tasks": [{"status": "DONE", "verification_status": "FAILED"}]},
        source="state/current.yaml",
    )

    findings = find_done_tasks_with_failed_verification([state])

    assert findings[0].message == (
        "task <unknown> is DONE with FAILED verification (state/current.yaml)"
    )
