# Operational Metamodel V1 — PROPOSED

Status: PROPOSED
Authority: becomes normative only if `DEC-003` is approved, the complete TR-MODEL-EXTEND candidate passes required checks, and the candidate is promoted to the baseline.

## Purpose

Define authoritative ownership, lifecycle, relationships, migration, discovery, and enforcement for operational project artifacts required by controlled and later semi-autonomous execution.

## Ownership matrix

| Fact category | Authoritative owner | Projection allowed elsewhere |
|---|---|---|
| requirement definition/status | `requirements/REQ-*.yaml` | yes |
| decision definition/status | `decisions/DEC-*.yaml` | yes |
| verification/validation result | `verification/VER-*.yaml` | yes |
| deferred work | `queue/QUEUE-*.yaml` | yes |
| diagnostic finding/root-cause lifecycle | `diagnostics/DIA-*.yaml` | yes |
| executable task lifecycle | `tasks/TASK-*.yaml` | yes |
| current project summary | `state/current.yaml` | n/a; projection only |

A projection MUST NOT contradict the authoritative owner. On conflict, the owned artifact is authoritative and the projection is stale/invalid.

## VER — Verification artifact

Purpose: persist attributable verification or validation evidence against a specific target and baseline.

Lifecycle: `PLANNED → RUNNING → PASSED | FAILED | NOT_VERIFIED | SUPERSEDED`.

Required semantics:
- unique `VER-*` ID;
- target and baseline are identifiable;
- method is explicit;
- result cannot be PASSED without evidence;
- referenced requirements/decisions/tasks must resolve when applicable;
- later contradictory evidence creates a new verification event; history is not rewritten.

Migration: existing `VER-001` is experimental/non-authoritative until it validates against the activated VER schema; after successful migration it may retain its ID and historical evidence.

## QUEUE — Deferred-work artifact

Purpose: persist intentionally deferred work that is not currently executable as an active task.

Lifecycle: `QUEUED → READY_FOR_TRIAGE → PROMOTED | CANCELLED | SUPERSEDED`.

Required semantics:
- unique `QUEUE-*` ID;
- objective/reason are explicit;
- resume/promote conditions are explicit when known;
- QUEUE is not a task and MUST NOT be represented as DOING;
- promotion to execution creates/links a TASK artifact rather than mutating QUEUE into a TASK identity.

Migration: existing `QUEUE-001` remains non-authoritative until schema-valid and explicitly migrated.

## DIA — Diagnostic artifact

Purpose: persist diagnostic reasoning without collapsing observations, hypotheses and root causes.

Lifecycle: `OBSERVED → INVESTIGATING → HYPOTHESIS → ROOT_CAUSE_CONFIRMED | ROOT_CAUSE_UNKNOWN → CLOSED_RESOLVED | CLOSED_ACCEPTED_UNKNOWN | CLOSED_NO_ACTION`.

Required semantics:
- observation/evidence remain distinguishable from hypotheses;
- a hypothesis MUST NOT be represented as confirmed root cause without supporting evidence;
- closure records corrective action, preventive action when applicable, verification, and residual risk/unknowns;
- related findings may reference common root causes but remain independently auditable.

The current TASK-003 investigation should be migrated into one or more DIA artifacts only after this model is activated.

## TASK — Executable task artifact

Purpose: own executable work lifecycle and provide deterministic input for future autonomous task selection.

Lifecycle: `TODO → READY → DOING → BLOCKED | DONE | CANCELLED`, with explicit reopening transition where needed.

Required semantics:
- unique `TASK-*` ID;
- objective, scope, baseline and acceptance/definition-of-done information are identifiable;
- dependencies and blockers are represented explicitly;
- ownership/claim is explicit while DOING;
- required authority is identifiable;
- DONE requires compatible verification state;
- TASK references verification rather than owning verification evidence;
- deferred/unready ideas belong in QUEUE, not TASK.

Task ownership decision: `tasks/TASK-*.yaml` is proposed as repository-native authoritative ownership. `state/current.yaml` may summarize task counts/active IDs but does not own task status.

Migration: TASK-001, TASK-002 and TASK-003 currently embedded in `state/current.yaml` must be migrated atomically with state projection changes before TASK becomes MODEL_ACTIVE.

## STATE — Project-state projection

`state/current.yaml` is a current-state projection for cold-start efficiency. It is not the owner of facts already owned by another artifact category.

It SHOULD contain:
- project identifier;
- current baseline identifier;
- overall project status;
- active task IDs;
- blocker/open-finding IDs;
- queued-work IDs;
- next-action summary;
- last projection update metadata.

It MUST NOT silently override owned statuses. Deterministically derivable values SHOULD eventually be generated or validated from authoritative artifacts.

## Relationships

- REQ may be implemented by TASK and verified by VER.
- DEC may authorize or constrain TASK/change transitions.
- TASK may depend on REQ/DEC/TASK and link to VER.
- DIA may produce corrective TASK and preventive TASK/DEC/REQ changes.
- QUEUE may be promoted into TASK through an explicit linkage.
- STATE projects active IDs and summary values from all owner categories.

## Discovery

Cold-start/bootstrap MUST know the active owner directories. After activation, `BOOTSTRAP.md` must direct agents to active TASK/DIA/QUEUE/VER artifacts relevant to current state rather than relying only on filesystem inference.

## Enforcement requirements

Before activation, the candidate MUST include:
- JSON schemas for VER, QUEUE, DIA and TASK;
- canonical templates/examples;
- validator registration for all four types;
- deterministic invariants and tests;
- migration of VER-001, QUEUE-001 and embedded TASK-001..003;
- updated state projection semantics;
- bootstrap/discovery update;
- successful compliance run on the complete candidate.

## Activation boundary

All mandatory components above MUST be promoted in one baseline change. If any mandatory component fails validation, all four types remain non-authoritative and current experimental instances remain historical/migration input only.
