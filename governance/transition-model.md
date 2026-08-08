# Transition Model V1 — PROPOSED

Status: PROPOSED
Authority: becomes normative only if `DEC-002` is approved and promoted to the project baseline.

## Purpose

This model governs significant state changes. It complements invariants: invariants define what must remain true; transitions define how the system is allowed to change while preserving those invariants.

A significant transition MUST be describable through the contract below before it becomes enforceable or promotable to baseline.

## Transition contract

Each significant transition SHOULD define:

- `id` — persistent transition identifier;
- `from` — allowed source state(s);
- `to` — allowed destination state(s);
- `trigger` — event or explicit instruction initiating the transition;
- `preconditions` — conditions that MUST hold before execution;
- `required_authority` — minimum authority level;
- `required_evidence` — evidence required before promotion;
- `actions` — permitted operations;
- `atomic_changes` — repository elements that MUST change as one logical unit;
- `postconditions` — conditions that MUST hold after success;
- `validation` — checks proving the transition succeeded;
- `failure_behavior` — required behavior on failure;
- `rollback` — recovery behavior when applicable;
- `persistence` — records that MUST be written;
- `audit` — evidence needed to reconstruct who/what/why/how.

If a mandatory element is unknown and materially affects correctness, the transition MUST NOT be promoted to its destination state.

## Global transition rules

### TR-GEN-001 — Explicit source and destination
A significant state change MUST identify its source and destination states.

### TR-GEN-002 — Preconditions before side effects
Mandatory preconditions MUST be evaluated before irreversible or externally visible side effects.

### TR-GEN-003 — Authority before execution
The required authority MUST be established before executing a transition whose effects exceed the agent's current authority.

### TR-GEN-004 — Atomic logical changes
Changes that jointly establish one new state SHOULD be treated as one logical transaction. Partial completion MUST NOT be represented as successful promotion.

### TR-GEN-005 — Postcondition verification
A transition MUST NOT be considered successful until mandatory postconditions are verified.

### TR-GEN-006 — Failure preserves truth
On failure, the repository MUST represent the actual state, not the intended state. Retry MUST begin from the observed current state.

### TR-GEN-007 — Auditability
Successful significant transitions SHOULD preserve sufficient evidence to reconstruct trigger, baseline, authority, changes, validation, and result.

### TR-GEN-008 — No silent transition
An artifact MUST NOT silently cross a governance-significant boundary such as PROPOSED→APPROVED, WORKING→BASELINE, FAILED→PASSED, or UNKNOWN→CONFIRMED.

## Core transitions

### TR-DEC-APPROVE — Decision approval

FROM: `PROPOSED`
TO: `APPROVED`

Trigger:
- explicit approval by an authority permitted to approve the decision.

Preconditions:
- decision artifact exists and matches schema;
- problem and proposed decision are explicit;
- material conflicts are resolved or explicitly accepted;
- required impact analysis exists when applicable.

Authority:
- minimum level determined by affected scope; A3 for project-level decisions unless a stricter rule applies.

Required evidence:
- approval evidence;
- rationale;
- impact evidence when required.

Atomic changes:
- decision status becomes `APPROVED`;
- approval evidence is persisted;
- affected state or references are updated when necessary.

Postconditions:
- decision is authoritative according to governance precedence;
- no superseded decision remains current where the new decision replaces it.

Failure behavior:
- remain `PROPOSED`.

### TR-TASK-START — Task start

FROM: `TODO`
TO: `DOING`

Trigger:
- agent or human starts the task.

Preconditions:
- objective is known;
- scope is bounded enough to execute;
- blocking dependencies are resolved or explicitly accepted;
- baseline is identified;
- required authority is available.

Postconditions:
- task is represented as `DOING`;
- active baseline and ownership are identifiable when relevant.

Failure behavior:
- remain `TODO` or become `BLOCKED` if a blocker is discovered.

### TR-TASK-COMPLETE — Task completion

FROM: `DOING`
TO: `DONE`

Preconditions:
- implementation work is complete;
- mandatory verification has not failed;
- required persistence/documentation is complete;
- unresolved blockers do not invalidate completion.

Required evidence:
- verification result or explicit `NOT_REQUIRED` justification.

Postconditions:
- task status is `DONE`;
- verification status is compatible with completion;
- next state/work is updated where applicable.

Failure behavior:
- remain `DOING` or become `BLOCKED`.

### TR-VERIFY — Verification promotion

FROM: `IMPLEMENTED` or unverified state
TO: `VERIFIED`

Preconditions:
- verification method is defined;
- evidence is obtainable or inability is explicitly recorded.

Required evidence:
- actual test/check results.

Postconditions:
- result is persisted as PASS/FAIL/NOT_VERIFIED;
- no PASS is recorded without evidence.

Failure behavior:
- remain unverified or record failed verification; MUST NOT promote to VERIFIED.

### TR-VALIDATE — Requirement validation

FROM: `VERIFIED`
TO: `VALIDATED`

Preconditions:
- relevant requirement and acceptance criteria are known;
- technical verification evidence exists.

Required evidence:
- explicit comparison of result against acceptance criteria.

Postconditions:
- requirement satisfaction result is persisted.

Failure behavior:
- remain VERIFIED but NOT VALIDATED, or record validation failure.

### TR-BASELINE-PROMOTE — Candidate to approved baseline

FROM: `WORKING` or `CANDIDATE`
TO: `BASELINE`

Trigger:
- promotion request.

Preconditions:
- candidate baseline is identifiable;
- required tests/compliance checks pass;
- significant decisions are approved;
- no unresolved mandatory invariant violation exists;
- required human gate is satisfied;
- rollback/recovery is defined when required.

Authority:
- at least the level required by the highest-impact contained change.

Required evidence:
- candidate identifier;
- compliance result;
- test/validation result;
- approval evidence when required.

Atomic changes:
- baseline pointer moves to candidate;
- project state reflects the promoted baseline;
- superseded baseline remains reconstructible through history.

Postconditions:
- `main`/designated baseline ref represents the approved state;
- required checks remain satisfied.

Failure behavior:
- candidate remains non-baseline; existing baseline is unchanged.

### TR-MODEL-EXTEND — Activate a new artifact type

FROM: `CONCEPT_PROPOSED`
TO: `MODEL_ACTIVE`

Trigger:
- need for a new persistent artifact type or lifecycle concept.

Preconditions:
- purpose and ownership are defined;
- lifecycle/states are defined;
- relationships to existing artifact types are defined;
- source-of-truth semantics are defined;
- migration/backward-compatibility impact is assessed.

Required evidence:
- normative definition;
- schema when machine-structured;
- template/example when appropriate;
- invariants;
- validator/compliance impact assessment;
- tests for enforceable rules;
- bootstrap/discovery impact assessment;
- successful validation of the complete metamodel change.

Atomic changes:
- all mandatory metamodel components are promoted together.

Postconditions:
- the artifact type is officially ACTIVE;
- agents may create production instances of the type;
- validators and discovery mechanisms understand it where required.

Failure behavior:
- type remains `CONCEPT_PROPOSED`;
- production instances MUST NOT be created as authoritative artifacts.

This transition directly addresses RC-01.

### TR-DIAG-CLOSE — Close a diagnostic finding

FROM: `OBSERVED` / `HYPOTHESIS` / `ROOT_CAUSE_CONFIRMED`
TO: `CLOSED`

Preconditions:
- observation is recorded;
- unsupported hypotheses are not represented as causes;
- root cause is confirmed or explicitly remains UNKNOWN;
- corrective action is identified when needed;
- preventive/root-cause action is identified when applicable;
- verification of the corrective/preventive result exists or is explicitly pending.

Postconditions:
- closure reason is explicit;
- residual risks/unknowns remain visible;
- related follow-up work is tracked.

Failure behavior:
- finding remains open.

## Knowledge ownership principle — proposed

To avoid state drift, each persistent fact SHOULD have one authoritative owner category. Other files MAY project or summarize that fact but MUST NOT become competing authorities.

Initial ownership proposal:

- `requirements/` owns requirement definitions and status;
- `decisions/` owns decision definitions and approval status;
- `verification/` should own formal verification results once that artifact type is formally activated;
- `queue/` should own deferred-work records once that artifact type is formally activated;
- task lifecycle ownership remains unresolved and MUST be decided before autonomous execution;
- `state/current.yaml` should be a current-state projection, not the primary owner of facts already owned elsewhere.

This section intentionally leaves unresolved ownership as explicit UNKNOWN rather than silently deciding it.

## Migration rule

Approval of this model does NOT automatically validate existing `VER-*` or `QUEUE-*` artifacts. After approval, existing unsupported artifact types MUST undergo `TR-MODEL-EXTEND` or be migrated/retired through an explicit change.

## Acceptance criteria for Transition Model V1

Before `DEC-002` may be approved, reviewers SHOULD verify that:

1. RC-00 is addressed by a generic transition contract rather than local patches.
2. RC-01 is prevented by `TR-MODEL-EXTEND`.
3. RC-02 is addressed by `TR-BASELINE-PROMOTE` and a candidate/baseline distinction.
4. Failure paths preserve the actual current state.
5. The model does not silently resolve H-03 where evidence is insufficient.
6. Existing Governance V1.0 invariants remain compatible or required changes are explicitly identified.
7. Implementation work is deferred until the model is approved.
