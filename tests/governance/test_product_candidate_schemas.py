from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from ai_governance.infrastructure.repository_registry import ARTIFACT_TYPES


REPO = Path(__file__).resolve().parents[2]
SCHEMAS = REPO / "schemas"


def load_schema(name: str) -> dict:
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def validator_for(name: str) -> Draft202012Validator:
    reference_schema = load_schema("typed-reference.schema.json")
    registry = Registry().with_resource(
        "typed-reference.schema.json",
        Resource.from_contents(reference_schema),
    )
    return Draft202012Validator(load_schema(name), registry=registry)


def assert_valid(name: str, instance: dict) -> None:
    errors = list(validator_for(name).iter_errors(instance))
    assert not errors, "\n".join(error.message for error in errors)


def test_typed_reference_schema_accepts_three_reference_kinds() -> None:
    validator = Draft202012Validator(load_schema("typed-reference.schema.json"))
    valid = [
        {"kind": "artifact", "target": "REQ-001"},
        {"kind": "element", "target": "SYS-001", "element": "component.execution"},
        {"kind": "implementation", "target_type": "test", "target": "tests/unit/test_risk.py"},
    ]
    for item in valid:
        assert not list(validator.iter_errors(item))


def test_typed_reference_schema_rejects_ambiguous_or_untyped_references() -> None:
    validator = Draft202012Validator(load_schema("typed-reference.schema.json"))
    invalid = [
        {"target": "REQ-001"},
        {"kind": "element", "target": "REQ-001", "element": "component.execution"},
        {"kind": "implementation", "target": "src/x.py"},
    ]
    for item in invalid:
        assert list(validator.iter_errors(item))


def test_minimal_system_candidate_is_schema_valid() -> None:
    assert_valid(
        "system.schema.json",
        {
            "id": "SYS-001",
            "status": "PROPOSED",
            "title": "Trading micro-slice",
            "purpose": "Define the structural boundary of the candidate micro-slice.",
            "boundary": {
                "in_scope": ["market data to broker order path"],
                "out_of_scope": ["production deployment"],
                "external_actors": ["market data provider", "broker"],
            },
            "capabilities": [
                {
                    "id": "capability.risk_control",
                    "name": "Risk control",
                    "responsibility": "Gate orders before submission.",
                    "owner_component": "component.risk_gate",
                }
            ],
            "components": [
                {
                    "id": "component.risk_gate",
                    "name": "Risk gate",
                    "responsibilities": ["Evaluate pre-trade risk constraints."],
                }
            ],
            "interfaces": [
                {
                    "id": "interface.broker",
                    "provider": "external.broker",
                    "consumer": "component.order_manager",
                    "contract": "Submit and receive order lifecycle messages.",
                }
            ],
            "data": [
                {
                    "id": "data.order",
                    "name": "Order",
                    "owner": "component.order_manager",
                    "semantics": "Order intent and lifecycle state.",
                }
            ],
            "configuration": [
                {
                    "id": "config.risk_limit",
                    "name": "Risk limit",
                    "behavioral_effect": "Changes whether an order may pass the risk gate.",
                }
            ],
            "traceability": [
                {"kind": "artifact", "target": "REQ-001"},
            ],
        },
    )


def test_minimal_behavior_candidate_is_schema_valid() -> None:
    assert_valid(
        "behavior.schema.json",
        {
            "id": "BEH-001",
            "status": "PROPOSED",
            "title": "Pre-trade order submission",
            "scenario": "A candidate order is risk-checked before broker submission.",
            "system_elements": [
                {"kind": "element", "target": "SYS-001", "element": "component.risk_gate"}
            ],
            "preconditions": ["Market data is fresh."],
            "inputs": ["candidate order", "portfolio state"],
            "outputs": ["submitted order or rejection"],
            "states": [
                {"id": "state.candidate", "name": "Candidate"},
                {"id": "state.submitted", "name": "Submitted"},
                {"id": "state.rejected", "name": "Rejected", "terminal": True},
            ],
            "transitions": [
                {
                    "id": "transition.submit",
                    "source": "state.candidate",
                    "trigger": "risk check passes",
                    "target": "state.submitted",
                }
            ],
            "runtime_invariants": [
                {
                    "id": "invariant.risk_limit",
                    "condition": "Order risk must not exceed configured pre-trade limit.",
                    "target": {"kind": "element", "target": "SYS-001", "element": "component.risk_gate"},
                }
            ],
            "failure_modes": [
                {
                    "id": "failure.stale_market_data",
                    "condition": "Market data is stale.",
                    "detection": "Freshness threshold is exceeded.",
                    "action": "Reject the candidate order.",
                    "resulting_state": "state.rejected",
                }
            ],
            "verification": {
                "criteria": ["No order reaches submitted state when the risk invariant fails."]
            },
            "traceability": [
                {"kind": "artifact", "target": "REQ-001"}
            ],
        },
    )


def test_sys_and_beh_are_not_active_repository_artifact_types_yet() -> None:
    assert "SYS" not in ARTIFACT_TYPES
    assert "BEH" not in ARTIFACT_TYPES
