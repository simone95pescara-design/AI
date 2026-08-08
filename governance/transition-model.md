# Transition Model V1 — PROPOSED

Status: PROPOSED
Authority: this document becomes normative only after `DEC-002` is explicitly approved, all mandatory candidate checks pass, and the approved candidate is promoted to the designated baseline branch.

## Purpose

This model governs governance-significant state changes. Invariants define what must remain true; transitions define how the system is allowed to change while preserving those invariants.

A governance-significant state change MUST use a defined transition before it can be represented as successfully promoted.

## Transition contract

Every governance-significant transition MUST define:

- `id` — persistent transition identifier;
- `version` — version of the transition definition;
- `from` — allowed source state(s);
- `to` — allowed destination state(s);
- `trigger` — event or explicit instruction initiating the transition;
- `preconditions` — conditions that MUST hold before execution;
- `required_authority` — minimum authority level;
- `required_evidence` — evidence required for successful promotion;
- `actions` — permitted operations;
- `atomic_changes` — elements that establish the new logical state together;
- `postconditions` — conditions that MUST hold after success;
- `validation` — checks proving the transition succeeded;
- `failure_behavior` — required behavior on failure;
- `persistence` — records that MUST be written or updated;
- `audit` — evidence needed to reconstruct trigger, baseline, authority, change and result.

The following fields MUST also be defined when applicable and MUST explicitly state `NOT_APPLICABLE` when intentionally omitted for a significant transition:

- `rollback`;
- `migration`;
- `external_effects`;
- `human_gate`.

If a mandatory element is unknown and materially affects correctness, the transition MUST NOT be promoted to its destination state.

## State planes

The model distinguishes four planes:

- `WORKING` — mutable work not eligible to represent the approved project baseline;
- `CANDIDATE` — a bounded working state submitted for validation/promotion;
- `APPROVED_CANDIDATE` — a candidate for which required human/project decisions are approved but baseline promotion has not yet occurred;
- `BASELINE` — the designated authoritative repository state after successful promotion.

For the current GitHub implementation proposal:

- feature/working branches represent `WORKING`;
- an open PR targeting the baseline branch represents `CANDIDATE`;
- approval of required decisions can make the PR logically `APPROVED_CANDIDATE`;
- merge into the designated baseline branch after mandatory checks represents baseline promotion.

Human approval alone MUST NOT make candidate content normative. CI success alone MUST NOT make candidate content normative. Normative activation requires successful baseline promotion.

## Global transition rules

### TR-GEN-001 — Explicit source and destination
A governance-significant state change MUST identify source and destination states.

### TR-GEN-002 — Preconditions before side effects
Mandatory preconditions MUST be evaluated before irreversible or externally visible side effects.

### TR-GEN-003 — Authority before execution
Required authority MUST be established before executing a transition whose effects exceed the agent's current authority.

### TR-GEN-004 — Authority aggregation
For a composed change, required authority equals the highest authority required by any contained mandatory transition or affected high-impact operation. A lower-level transition MUST NOT reduce the authority required by another contained transition.

### TR-GEN-005 — Atomic logical changes
Changes that jointly establish one new logical state MUST be treated as one logical transaction for promotion purposes. Partial completion MUST NOT be represented as successful promotion.

### TR-GEN-006 — Postcondition verification
A transition MUST NOT be considered successful until mandatory postconditions are verified.

### TR-GEN-007 — Failure preserves truth
On failure, the repository MUST represent the observed actual state, not the intended state. Retry MUST begin from the observed current state.

### TR-GEN-008 — Auditability
Successful governance-significant transitions MUST preserve sufficient evidence to reconstruct trigger, baseline, authority, changes, validation and result.

### TR-GEN-009 — No silent transition
An artifact MUST NOT silently cross a governance-significant boundary such as `PROPOSED→APPROVED`, `CANDIDATE→BASELINE`, `FAILED→PASSED`, `UNKNOWN→CONFIRMED`, or `CONCEPT_PROPOSED→MODEL_ACTIVE`.

### TR-GEN-010 — Transition definition lifecycle
Transition definitions themselves are governed knowledge. A transition definition MUST have an ID and version, and a materially changed transition definition MUST be reviewed as a governance change before replacing the active definition. Superseded transition definitions MUST remain reconstructible through version history.

### TR-GEN-011 — Transition composition
When multiple transitions are required for one objective, an orchestration plan MUST identify:

- component transitions;
- execution order or safe parallelism;
- shared preconditions;
- aggregate authority;
- atomic promotion boundary;
- failure/rollback behavior across component transitions.

A composed transition MUST NOT be promoted if any mandatory component transition has failed or remains materially UNKNOWN.

### TR-GEN-012 — Non-active artifact types are non-authoritative
An artifact type that has not completed `TR-MODEL-EXTEND` MUST NOT become an authoritative source of project truth. Existing experimental instances MAY be retained as evidence or migration input but MUST be marked non-authoritative until activated or retired.

## Core transitions

### TR-DEC-APPROVE v1 — Decision approval

FROM: `PROPOSED`
TO: `APPROVED`

Trigger:
- explicit approval by an authority permitted to approve the decision.

Preconditions:
- decision artifact exists and matches the active schema;
- problem and proposed decision are explicit;
- material conflicts are resolved or explicitly accepted;
- required impact analysis exists when applicable.

Required authority:
- minimum level determined by affected scope; A3 for project-level decisions unless a stricter rule applies.

Required evidence:
- approval evidence;
- rationale;
- impact evidence when required.

Actions:
- record approval without yet implying baseline promotion.

Atomic changes:
- decision status becomes `APPROVED`;
- approval evidence is persisted;
- directly dependent candidate references are updated where required.

Postconditions:
- decision is approved within the candidate state;
- supersession relationships are coherent.

Validation:
- decision schema and decision invariants pass.

Failure behavior:
- remain `PROPOSED`.

Persistence:
- decision artifact and approval evidence.

Audit:
- approver/approval evidence, candidate baseline, affected items.

Rollback: status may return to a non-approved state only through an explicit subsequent governance transition; history MUST remain reconstructible.
Migration: NOT_APPLICABLE.
External effects: NOT_APPLICABLE unless the decision itself authorizes a later external-effect transition.
Human gate: required when governance/authority policy requires explicit human approval.

### TR-TASK-START v1 — Task start

Status: PROVISIONAL; MUST NOT become enforceable until authoritative task ownership is defined.

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

Required authority:
- aggregate authority of intended work.

Required evidence:
- task objective, baseline and readiness evidence appropriate to task impact.

Actions:
- claim/start task according to the future authoritative task model.

Atomic changes:
- task status and ownership/start metadata once task ownership is defined.

Postconditions:
- task is represented as `DOING`;
- active baseline and ownership are identifiable.

Validation:
- task readiness and ownership checks.

Failure behavior:
- remain `TODO` or become `BLOCKED` if a blocker is discovered.

Persistence:
- future authoritative task record.

Audit:
- starter/agent, baseline, scope, authority.

Rollback: return to TODO only through an explicit task transition; partial work must remain visible where relevant.
Migration: pending task-model decision.
External effects: governed by contained work transitions.
Human gate: according to aggregate authority.

### TR-TASK-COMPLETE v1 — Task completion

Status: PROVISIONAL; MUST NOT become enforceable until authoritative task ownership is defined.

FROM: `DOING`
TO: `DONE`

Preconditions:
- implementation work is complete;
- mandatory verification has not failed;
- required persistence/documentation is complete;
- unresolved blockers do not invalidate completion.

Required authority:
- authority required by contained work and completion gate.

Required evidence:
- verification result or explicit `NOT_REQUIRED` justification where allowed.

Actions:
- close the authoritative task record.

Atomic changes:
- task status, verification linkage, open-work projection.

Postconditions:
- task status is `DONE`;
- verification status is compatible with completion;
- next state/work is updated where applicable.

Validation:
- Definition of Done checks.

Failure behavior:
- remain `DOING` or become `BLOCKED`.

Persistence:
- future authoritative task record plus verification links.

Audit:
- result, evidence, baseline, residual work.

Rollback: completion reversal requires an explicit reopening transition.
Migration: pending task-model decision.
External effects: NOT_APPLICABLE unless contained change requires them.
Human gate: according to aggregate authority.

### TR-VERIFY v1 — Verification promotion

FROM: `IMPLEMENTED` or explicit unverified state
TO: `VERIFIED`

Trigger:
- request to verify a defined result.

Preconditions:
- verification method is defined;
- verification target/baseline is identifiable;
- evidence is obtainable or inability is explicitly recorded.

Required authority:
- sufficient authority to execute the verification method; verification does not itself authorize unrelated project decisions.

Required evidence:
- actual test/check results.

Actions:
- execute verification and record result.

Atomic changes:
- verification evidence and linked verification status.

Postconditions:
- PASS/FAIL/NOT_VERIFIED is persisted;
- no PASS exists without evidence.

Validation:
- evidence is attributable to the declared target/baseline.

Failure behavior:
- remain unverified or record failed verification; MUST NOT promote to VERIFIED.

Persistence:
- authoritative verification record only after the verification artifact type has completed `TR-MODEL-EXTEND`.

Audit:
- method, target, baseline, result, evidence.

Rollback: NOT_APPLICABLE; later contradictory evidence requires a new verification event, not deletion of history.
Migration: existing `VER-*` records require explicit model activation/migration.
External effects: according to verification tooling.
Human gate: NOT_APPLICABLE unless verification uses a higher-authority tool/environment.

### TR-VALIDATE v1 — Requirement validation

FROM: `VERIFIED`
TO: `VALIDATED`

Trigger:
- request to establish requirement satisfaction.

Preconditions:
- relevant approved requirement and acceptance criteria are known;
- technical verification evidence exists;
- verification target is compatible with the requirement baseline.

Required authority:
- validation authority required by the affected requirement/project gate.

Required evidence:
- explicit comparison of result against acceptance criteria.

Actions:
- evaluate evidence against requirement criteria.

Atomic changes:
- validation result and required requirement/status projections.

Postconditions:
- requirement satisfaction result is persisted.

Validation:
- acceptance criteria are individually accounted for or explicitly unresolved.

Failure behavior:
- remain VERIFIED but NOT VALIDATED, or record validation failure.

Persistence:
- validation evidence linked to requirement and verification evidence.

Audit:
- requirement version, evidence, evaluator, result.

Rollback: NOT_APPLICABLE; later evidence produces a new validation event.
Migration: depends on activated verification/validation artifact model.
External effects: NOT_APPLICABLE.
Human gate: when requirement acceptance requires explicit human/project-owner acceptance.

### TR-BASELINE-PROMOTE v1 — Candidate to approved baseline

FROM: `CANDIDATE` or `APPROVED_CANDIDATE`
TO: `BASELINE`

Trigger:
- explicit promotion request/merge action.

Preconditions:
- candidate identifier is immutable/identifiable;
- required tests/compliance checks pass against the candidate merged with current baseline where applicable;
- significant contained decisions are approved;
- no unresolved mandatory invariant violation exists;
- required human gate is satisfied;
- rollback/recovery is defined when required;
- baseline has not changed incompatibly since candidate validation, or the candidate has been revalidated against the new baseline.

Required authority:
- highest authority required by any contained mandatory transition or affected operation.

Required evidence:
- candidate identifier;
- current baseline identifier;
- compliance result;
- test/validation result;
- approval evidence when required.

Actions:
- promote candidate through the designated baseline mechanism.

Atomic changes:
- baseline ref/pointer moves to promoted candidate;
- project-state projection is updated as part of or immediately after the same logical promotion;
- superseded baseline remains reconstructible through version history.

Postconditions:
- designated baseline ref represents the approved state;
- mandatory checks remain satisfied for the promoted baseline;
- candidate content is now normative according to governance precedence.

Validation:
- verify actual baseline ref/commit and mandatory post-merge checks if required.

Failure behavior:
- existing baseline remains authoritative; candidate remains non-baseline and actual partial state is recorded.

Persistence:
- merge/promotion record, relevant approvals, validation evidence and updated state projection.

Audit:
- source candidate, previous baseline, promoted baseline, checks, approvals.

Rollback: explicit baseline recovery/revert transition required if promotion must be undone.
Migration: NOT_APPLICABLE.
External effects: baseline branch/ref mutation and downstream effects triggered by it.
Human gate: required whenever aggregate authority or branch policy requires it.

### TR-MODEL-EXTEND v1 — Activate a new artifact type

FROM: `CONCEPT_PROPOSED`
TO: `MODEL_ACTIVE`

Trigger:
- need for a new persistent artifact type or lifecycle concept.

Preconditions:
- purpose and authoritative ownership are defined;
- lifecycle/states are defined;
- relationships to existing artifact types are defined;
- source-of-truth semantics are defined;
- migration/backward-compatibility impact is assessed;
- mandatory metamodel components are identified using the applicability rules below.

Required authority:
- A3 minimum because activation changes project governance/metamodel; stricter authority applies if the type governs critical operations.

Required evidence — always mandatory:
- normative definition;
- ownership/source-of-truth rule;
- lifecycle/state definition;
- relationship definition;
- invariants or an explicit determination that no new invariant is required;
- compliance/validator impact assessment;
- bootstrap/discovery impact assessment;
- migration/backward-compatibility assessment;
- validation showing all mandatory components are coherent.

Required evidence — conditional:
- machine schema: MUST exist when instances are machine-structured and schema validation is feasible;
- template/example: MUST exist when agents/humans need a canonical creation format;
- validator implementation: MUST exist for deterministic enforceable rules; otherwise the rule must be classified non-enforceable/observable;
- automated tests: MUST exist for implemented deterministic validation behavior;
- registry/index update: MUST exist when discovery is not already deterministic without it.

Actions:
- introduce all mandatory metamodel components as one candidate change.

Atomic changes:
- all mandatory model components are promoted together; no authoritative instance may precede model activation.

Postconditions:
- artifact type is officially `MODEL_ACTIVE`;
- agents may create authoritative production instances;
- validators and discovery mechanisms understand the type where required.

Validation:
- metamodel completeness checklist and all deterministic compliance tests pass.

Failure behavior:
- type remains `CONCEPT_PROPOSED`;
- instances MUST NOT be treated as authoritative.

Persistence:
- normative model definition and required supporting components.

Audit:
- rationale, owner, lifecycle, components, migration, checks, activating baseline.

Rollback: retiring or replacing an active type requires an explicit model-change transition preserving migration/history.
Migration: mandatory assessment; migration plan required when existing data/artifacts are affected.
External effects: NOT_APPLICABLE unless model activation changes external integrations.
Human gate: A3 approval minimum.

This transition directly addresses RC-01.

### TR-DIAG-CLOSE v1 — Close a diagnostic finding

FROM: `OBSERVED`, `HYPOTHESIS`, or `ROOT_CAUSE_CONFIRMED`
TO: one of `CLOSED_RESOLVED`, `CLOSED_ACCEPTED_UNKNOWN`, `CLOSED_DEFERRED`

Trigger:
- request to close or disposition a diagnostic finding.

Preconditions:
- observation is recorded;
- unsupported hypotheses are not represented as causes;
- known evidence is recorded;
- corrective action is identified when needed;
- preventive/root-cause action is identified when applicable;
- unresolved unknowns/risks are explicit.

Required authority:
- authority appropriate to accept residual risk or close the affected issue.

Required evidence:
- closure outcome and rationale;
- verification evidence for `CLOSED_RESOLVED`;
- explicit accepted unknown/risk for `CLOSED_ACCEPTED_UNKNOWN`;
- tracked follow-up/defer reason for `CLOSED_DEFERRED`.

Actions:
- assign explicit closure outcome without rewriting diagnostic history.

Atomic changes:
- diagnostic state, residual risk/unknown references, follow-up links.

Postconditions:
- closure reason is explicit;
- residual risks/unknowns remain visible;
- related follow-up work is tracked where applicable.

Validation:
- closure outcome requirements are satisfied.

Failure behavior:
- finding remains open.

Persistence:
- authoritative diagnostic artifact only after the diagnostic artifact type completes `TR-MODEL-EXTEND`.

Audit:
- observations, hypotheses, tests, evidence, conclusion, actions, closure authority.

Rollback: reopening requires an explicit diagnostic-reopen transition preserving closure history.
Migration: current conversational diagnostics remain evidence input until a diagnostic artifact model is activated.
External effects: NOT_APPLICABLE.
Human gate: required when accepting material residual risk/unknown beyond delegated authority.

## Knowledge ownership principle — proposed

Each persistent fact SHOULD have one authoritative owner category. Other files MAY project or summarize that fact but MUST NOT become competing authorities.

Initial ownership proposal:

- `requirements/` owns requirement definitions and approval/lifecycle status;
- `decisions/` owns decision definitions and approval/lifecycle status;
- `verification/` may own formal verification results only after the verification artifact type is activated through `TR-MODEL-EXTEND`;
- `queue/` may own deferred-work records only after the queue artifact type is activated through `TR-MODEL-EXTEND`;
- task lifecycle ownership remains UNKNOWN and MUST be decided before task transitions become enforceable;
- `state/current.yaml` is proposed as a current-state projection and MUST NOT override facts owned by an authoritative source category.

Where two representations conflict, the authoritative owner must prevail and the projection conflict must be reported rather than silently reconciled.

## Migration rule

Approval of this model does NOT automatically validate existing `VER-*`, `QUEUE-*`, or future unsupported artifact types. After normative promotion, each unsupported type MUST undergo `TR-MODEL-EXTEND` or be explicitly migrated/retired. Until then, its existing instances are non-authoritative evidence only.

## Promotion rule for this proposal

`DEC-002` approval and Transition Model activation are separate events:

1. reviewer/human approval may transition `DEC-002` from `PROPOSED` to `APPROVED` on the candidate branch;
2. mandatory compliance/review checks must pass against the current baseline;
3. the candidate may then undergo `TR-BASELINE-PROMOTE` through merge into the designated baseline branch;
4. only after successful promotion does this document become normative.

If baseline `main` changes before promotion, the candidate MUST be re-evaluated/revalidated against the updated baseline when the change could affect correctness.

## Acceptance criteria for Transition Model V1

Before `DEC-002` may be approved, reviewers MUST verify that:

1. RC-00 is addressed by a generic transition contract rather than local patches;
2. RC-01 is prevented by `TR-MODEL-EXTEND`;
3. RC-02 is addressed by explicit WORKING/CANDIDATE/BASELINE planes and `TR-BASELINE-PROMOTE`;
4. failure paths preserve actual current state;
5. H-03 is not silently resolved where evidence is insufficient;
6. mandatory versus conditional metamodel components are explicit;
7. transition definition versioning and composed transitions are governed;
8. non-active artifact types cannot become authoritative;
9. decision approval is distinct from normative baseline promotion;
10. existing Governance V1.0 invariants remain compatible or required changes are explicitly identified;
11. implementation/migration work beyond this candidate model is deferred until normative promotion.
