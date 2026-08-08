from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

REPO = Path(__file__).resolve().parents[1]
REQUIRED = [
    REPO / "AGENTS.md",
    REPO / "BOOTSTRAP.md",
    REPO / "governance" / "SPECIFICATION.md",
    REPO / "governance" / "authority.md",
    REPO / "governance" / "knowledge-policy.md",
    REPO / "governance" / "response-protocol.md",
    REPO / "governance" / "invariants.md",
    REPO / "governance" / "transition-model.md",
]
SCHEMAS = {
    "DEC": REPO / "schemas" / "decision.schema.json",
    "REQ": REPO / "schemas" / "requirement.schema.json",
    "RISK": REPO / "schemas" / "risk.schema.json",
    "STATE": REPO / "schemas" / "state.schema.json",
    "VER": REPO / "schemas" / "verification.schema.json",
    "QUEUE": REPO / "schemas" / "queue.schema.json",
    "DIA": REPO / "schemas" / "diagnostic.schema.json",
    "TASK": REPO / "schemas" / "task.schema.json",
}
ARTIFACT_ROOTS = {
    "DEC": REPO / "decisions",
    "REQ": REPO / "requirements",
    "RISK": REPO / "risks",
    "STATE": REPO / "state",
    "VER": REPO / "verification",
    "QUEUE": REPO / "queue",
    "DIA": REPO / "diagnostics",
    "TASK": REPO / "tasks",
}
ID_KIND = {prefix: prefix for prefix in ("DEC", "REQ", "RISK", "VER", "QUEUE", "DIA", "TASK")}
ID_PATTERN = re.compile(r"\b(?:DEC|REQ|RISK|VER|QUEUE|DIA|TASK)-\d{3,}\b")
SUPPORTED_SUFFIXES = {".yaml", ".yml", ".json"}
CLOSED_DIA = {"CLOSED_RESOLVED", "CLOSED_ACCEPTED_UNKNOWN", "CLOSED_NO_ACTION"}


def fail(code: str, message: str, errors: list[str]) -> None:
    errors.append(f"{code}: {message}")


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def check_required_files(errors: list[str]) -> None:
    for path in REQUIRED:
        if not path.exists():
            fail("CHECK-001", f"missing required file: {path.relative_to(REPO)}", errors)


def load_schema(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def check_schemas(errors: list[str]) -> None:
    for path in SCHEMAS.values():
        try:
            data = load_schema(path)
            Draft202012Validator.check_schema(data)
        except Exception as exc:
            fail("CHECK-002", f"invalid schema {path.relative_to(REPO)}: {exc}", errors)
            continue
        if data.get("type") != "object" or not data.get("required"):
            fail("CHECK-002", f"schema lacks object/required contract: {path.relative_to(REPO)}", errors)


def load_document(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    return json.loads(text) if path.suffix.lower() == ".json" else yaml.safe_load(text)


def load_artifacts(errors: list[str]) -> list[tuple[str, Path, dict[str, Any]]]:
    artifacts: list[tuple[str, Path, dict[str, Any]]] = []
    for kind, root in ARTIFACT_ROOTS.items():
        if not root.exists():
            continue
        schema = load_schema(SCHEMAS[kind])
        validator = Draft202012Validator(schema)
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in SUPPORTED_SUFFIXES:
                continue
            try:
                data = load_document(path)
            except Exception as exc:
                fail("CHECK-003", f"cannot parse {path.relative_to(REPO)}: {exc}", errors)
                continue
            if not isinstance(data, dict):
                fail("CHECK-003", f"artifact must be an object: {path.relative_to(REPO)}", errors)
                continue
            for err in sorted(validator.iter_errors(data), key=lambda item: list(item.absolute_path)):
                location = ".".join(str(part) for part in err.absolute_path) or "<root>"
                fail("CHECK-003", f"{path.relative_to(REPO)} [{location}]: {err.message}", errors)
            artifacts.append((kind, path, data))
    return artifacts


def check_duplicate_ids(artifacts: list[tuple[str, Path, dict[str, Any]]], errors: list[str]) -> None:
    seen: dict[str, Path] = {}
    for kind, path, data in artifacts:
        if kind == "STATE":
            continue
        item_id = data.get("id")
        if not isinstance(item_id, str):
            continue
        if item_id in seen and seen[item_id] != path:
            fail("INV-006", f"duplicate ID {item_id}: {seen[item_id].relative_to(REPO)} and {path.relative_to(REPO)}", errors)
        seen[item_id] = path


def extract_references(value: Any) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, str):
        refs.update(ID_PATTERN.findall(value))
    elif isinstance(value, list):
        for item in value:
            refs.update(extract_references(item))
    elif isinstance(value, dict):
        for item in value.values():
            refs.update(extract_references(item))
    return refs


def expected_kind(ref: str) -> str | None:
    prefix = ref.split("-", 1)[0]
    return ID_KIND.get(prefix)


def check_reference_integrity(item_id: str, data: dict[str, Any], indexed: dict[str, tuple[str, Path, dict[str, Any]]], rel: Path, errors: list[str]) -> None:
    for ref in extract_references(data):
        kind = expected_kind(ref)
        if kind is None:
            continue
        target = indexed.get(ref)
        if target is None:
            fail("INV-016", f"{item_id} references missing {kind} {ref} ({rel})", errors)
        elif target[0] != kind:
            fail("INV-016", f"{item_id} reference {ref} resolves to wrong type {target[0]}, expected {kind} ({rel})", errors)


def detect_task_cycle(graph: dict[str, list[str]]) -> list[str] | None:
    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        if node in visiting:
            i = stack.index(node)
            return stack[i:] + [node]
        if node in visited:
            return None
        visiting.add(node)
        stack.append(node)
        for dep in graph.get(node, []):
            if dep in graph:
                cycle = visit(dep)
                if cycle:
                    return cycle
        stack.pop()
        visiting.remove(node)
        visited.add(node)
        return None

    for node in graph:
        cycle = visit(node)
        if cycle:
            return cycle
    return None


def validate_semantics(artifacts: list[tuple[str, Path, dict[str, Any]]]) -> list[str]:
    errors: list[str] = []
    indexed: dict[str, tuple[str, Path, dict[str, Any]]] = {}
    for kind, path, data in artifacts:
        item_id = data.get("id")
        if kind != "STATE" and isinstance(item_id, str):
            indexed[item_id] = (kind, path, data)

    task_graph: dict[str, list[str]] = {}

    for kind, path, data in artifacts:
        rel = path.relative_to(REPO) if path.is_absolute() else path
        item_id = data.get("id", str(rel))
        status = data.get("status")

        if kind != "STATE" and isinstance(item_id, str):
            check_reference_integrity(item_id, data, indexed, rel, errors)

        if kind == "DEC":
            if status == "APPROVED" and not nonempty(data.get("rationale")):
                fail("INV-002", f"approved decision {item_id} has no rationale ({rel})", errors)
            if status == "SUPERSEDED":
                successor = data.get("superseded_by")
                if not nonempty(successor) or successor == item_id or successor not in indexed or indexed[successor][0] != "DEC":
                    fail("INV-003", f"superseded decision {item_id} has invalid successor {successor!r} ({rel})", errors)
            for predecessor in data.get("supersedes", []) or []:
                old = indexed.get(predecessor)
                if old is None or old[0] != "DEC":
                    fail("INV-007", f"decision {item_id} supersedes missing decision {predecessor} ({rel})", errors)
                elif old[2].get("status") != "SUPERSEDED" or old[2].get("superseded_by") != item_id:
                    fail("INV-007", f"decision {item_id} supersedes {predecessor}, but reciprocal supersession is not recorded", errors)

        if kind == "REQ":
            if status == "APPROVED" and not nonempty(data.get("verification_method")):
                fail("INV-005", f"approved requirement {item_id} has no verification_method ({rel})", errors)
            if status == "SUPERSEDED":
                successor = data.get("superseded_by")
                if not nonempty(successor) or successor == item_id or successor not in indexed or indexed[successor][0] != "REQ":
                    fail("INV-003", f"superseded requirement {item_id} has invalid successor {successor!r} ({rel})", errors)

        if kind == "VER":
            evidence = data.get("evidence") or []
            provenance = data.get("provenance") or {}
            if status == "PASSED" and not evidence:
                fail("INV-011", f"verification {item_id} is PASSED without evidence ({rel})", errors)
            if status == "PASSED" and not (nonempty(provenance.get("target")) and nonempty(provenance.get("baseline_ref"))):
                fail("INV-017", f"verification {item_id} is PASSED without structured target/baseline provenance ({rel})", errors)

        if kind == "TASK":
            deps = data.get("dependencies", []) or []
            task_graph[item_id] = deps
            if status == "DONE" and data.get("verification_status") == "FAILED":
                fail("INV-004", f"task {item_id} is DONE with FAILED verification ({rel})", errors)
            if status == "DOING" and not nonempty(data.get("owner")):
                fail("INV-012", f"task {item_id} is DOING without explicit owner ({rel})", errors)
            for dep in deps:
                target = indexed.get(dep)
                if target is None or target[0] != "TASK":
                    fail("INV-018", f"task {item_id} has missing/non-task dependency {dep} ({rel})", errors)
            if status == "READY":
                unresolved = [dep for dep in deps if indexed.get(dep) and indexed[dep][2].get("status") != "DONE"]
                if unresolved or data.get("blockers"):
                    fail("INV-018", f"task {item_id} is READY with unresolved dependencies/blockers: {unresolved or data.get('blockers')} ({rel})", errors)
            source = data.get("queue_source")
            if nonempty(source):
                queue = indexed.get(source)
                if queue is None or queue[0] != "QUEUE" or queue[2].get("status") != "PROMOTED" or queue[2].get("promoted_to") != item_id:
                    fail("INV-013", f"task {item_id} queue_source {source} is not reciprocally PROMOTED to this task ({rel})", errors)

        if kind == "QUEUE" and status == "PROMOTED":
            target = data.get("promoted_to")
            task = indexed.get(target) if nonempty(target) else None
            if task is None or task[0] != "TASK":
                fail("INV-013", f"queue item {item_id} is PROMOTED without valid TASK target ({rel})", errors)
            elif task[2].get("queue_source") != item_id:
                fail("INV-013", f"queue item {item_id} promotes {target}, but task does not reciprocally reference queue_source ({rel})", errors)

        if kind == "DIA":
            root_status = data.get("root_cause_status")
            root_cause = data.get("root_cause")
            if root_status == "CONFIRMED" and not nonempty(root_cause):
                fail("INV-014", f"diagnostic {item_id} confirms root cause without root_cause text ({rel})", errors)
            if root_status != "CONFIRMED" and status == "ROOT_CAUSE_CONFIRMED":
                fail("INV-014", f"diagnostic {item_id} status/root_cause_status conflict ({rel})", errors)
            if status in CLOSED_DIA:
                if not data.get("closure_reason"):
                    fail("INV-019", f"closed diagnostic {item_id} has no closure_reason ({rel})", errors)
                if status == "CLOSED_RESOLVED" and not data.get("verification"):
                    fail("INV-019", f"resolved diagnostic {item_id} has no closure verification ({rel})", errors)
                if status == "CLOSED_ACCEPTED_UNKNOWN" and not data.get("residual_risk"):
                    fail("INV-019", f"accepted-unknown diagnostic {item_id} has no residual risk ({rel})", errors)

        if kind == "STATE":
            for key, expected in (("active_tasks", "TASK"), ("queued_work", "QUEUE"), ("open_diagnostics", "DIA")):
                for ref in data.get(key, []) or []:
                    target = indexed.get(ref)
                    if target is None or target[0] != expected:
                        fail("INV-015", f"state projection {key} references missing {expected} {ref} ({rel})", errors)
                    elif key == "active_tasks" and target[2].get("status") not in {"READY", "DOING", "BLOCKED"}:
                        fail("INV-015", f"state active_tasks includes non-active {ref} status={target[2].get('status')} ({rel})", errors)
                    elif key == "queued_work" and target[2].get("status") not in {"QUEUED", "READY_FOR_TRIAGE"}:
                        fail("INV-015", f"state queued_work includes non-queued {ref} status={target[2].get('status')} ({rel})", errors)
                    elif key == "open_diagnostics" and target[2].get("status") in CLOSED_DIA:
                        fail("INV-015", f"state open_diagnostics includes closed {ref} ({rel})", errors)

    cycle = detect_task_cycle(task_graph)
    if cycle:
        fail("INV-018", f"task dependency cycle detected: {' -> '.join(cycle)}", errors)

    return errors


def check_obvious_secrets(errors: list[str]) -> None:
    patterns = [
        re.compile(r"AKIA[0-9A-Z]{16}"),
        re.compile(r"ghp_[A-Za-z0-9]{20,}"),
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    ]
    for path in REPO.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() not in {".md", ".py", ".json", ".yaml", ".yml", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in patterns:
            if pattern.search(text):
                fail("INV-008", f"possible secret in {path.relative_to(REPO)}", errors)


def main() -> int:
    errors: list[str] = []
    check_required_files(errors)
    check_schemas(errors)
    artifacts = load_artifacts(errors)
    check_duplicate_ids(artifacts, errors)
    errors.extend(validate_semantics(artifacts))
    check_obvious_secrets(errors)

    if errors:
        print("COMPLIANCE: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("COMPLIANCE: PASS")
    print("- schemas and artifact structures valid")
    print("- INV-016 persistent references resolve by type")
    print("- INV-017 PASSED verification has structured provenance")
    print("- INV-018 task dependencies are valid, acyclic and readiness-compatible")
    print("- INV-019 diagnostic closure preconditions are enforced")
    return 0


if __name__ == "__main__":
    sys.exit(main())
