# Transition Model V1 — APPROVED CANDIDATE

Status: APPROVED_CANDIDATE
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
- request to validate a verified result against an approved requirement.

Preconditions:
- relevant requirement and acceptance criteria are known;
- technical verification evidence exists and is attributable to the same candidate/baseline.

Required authority:
- sufficient authority to evaluate acceptance criteria; validation does not authorize baseline promotion.

Required evidence:
- explicit comparison of result against acceptance criteria.

Actions:
- evaluate requirement satisfaction.

Atomic changes:
- validation result and requirement-verification linkage.

Postconditions:
- requirement satisfaction result is persisted.

Validation:
- evidence covers mandatory acceptance criteria.

Failure behavior:
- remain VERIFIED but NOT VALIDATED, or record validation failure.

Persistence:
- authoritative validation/verification record after its model is activated.

Audit:
- requirement, acceptance criteria, evidence, result, candidate/baseline.

Rollback: NOT_APPLICABLE; later evidence creates a new validation event.
Migration: depends on verification-model activation.
External effects: NOT_APPLICABLE unless validation tooling causes them.
Human gate: only where acceptance criteria require human acceptance.

### TR-BASELINE-PROMOTE v1 — Approved candidate to baseline

FROM: `CANDIDATE` or `APPROVED_CANDIDATE`
TO: `BASELINE`

Trigger:
- promotion request after candidate review.

Preconditions:
- candidate baseline is uniquely identifiable;
- required tests/compliance checks pass against the current candidate;
- all decisions required for contained changes are `APPROVED`;
- no unresolved mandatory invariant violation exists;
- aggregate authority/human gates are satisfied;
- baseline target branch/ref is identified;
- rollback/recovery is defined when required;
- candidate is based on or reconciled with the current baseline so promotion does not silently discard intervening baseline changes.

Required authority:
- highest authority required by any contained transition or affected high-impact operation.

Required evidence:
- candidate/head identifier;
- current baseline identifier;
- successful compliance result for the promotion candidate;
- required test/validation results;
- approval evidence for contained decisions;
- reconciliation evidence when baseline changed during candidate work.

Actions:
- promote the approved candidate through the designated merge/promotion mechanism.

Atomic changes:
- designated baseline ref moves to promoted candidate result;
- baseline-facing project projection is updated as part of the promotion or an immediately required post-promotion transition;
- superseded baseline remains reconstructible in version history.

Postconditions:
- designated baseline ref represents the promoted state;
- promoted decisions/governance become authoritative only now;
- mandatory checks correspond to the promoted candidate;
- no required candidate content remains only on the working branch.

Validation:
- verify resulting baseline commit/ref and required post-promotion state.

Failure behavior:
- candidate remains non-baseline; existing baseline remains authoritative.

Persistence:
- merge/promotion history, baseline identifier, related decision/verification links.

Audit:
- source candidate, prior baseline, resulting baseline, approvals, CI/check results.

Rollback: explicit revert/rollback transition; history remains reconstructible.
Migration: NOT_APPLICABLE unless contained transitions require migration.
External effects: baseline branch/ref mutation; downstream automation may be triggered and must be considered in impact analysis.
Human gate: according to aggregate authority; governance changes require explicit approval.

### TR-MODEL-EXTEND v1 — Activate a new artifact type

FROM: `CONCEPT_PROPOSED`
TO: `MODEL_ACTIVE`

Trigger:
- need for a new persistent artifact type or lifecycle concept.

Preconditions:
- purpose is defined;
- authoritative ownership/source-of-truth semantics are defined;
- lifecycle/states and transitions are defined where applicable;
- relationships to existing artifact types are defined;
- migration/backward-compatibility impact is assessed;
- mandatory metamodel components for this artifact class are explicitly identified.

Required authority:
- A3 because this changes the project governance/metamodel; higher authority if security/data/production impact requires it.

Required evidence:
Mandatory for every new persistent artifact type:
- normative definition;
- ownership/source-of-truth definition;
- lifecycle/status semantics;
- relationship/discovery definition;
- invariant impact assessment;
- validator/compliance impact assessment;
- bootstrap/cold-start impact assessment;
- migration/backward-compatibility assessment;
- successful validation of the complete metamodel change.

Mandatory when applicable:
- machine-readable schema for structured machine-validated artifacts;
- canonical template/example for repeatable authored artifacts;
- automated validator checks for deterministic invariants;
- automated tests for enforceable rules;
- migration tooling for existing authoritative instances.

When a conditionally mandatory component is not applicable, the activation record MUST explain why.

Actions:
- implement all mandatory metamodel components as one governed candidate change.

Atomic changes:
- all components required for authoritative use are promoted in the same baseline promotion boundary.

Postconditions:
- artifact type is officially `MODEL_ACTIVE`;
- authoritative instances may now be created;
- validators/discovery/bootstrap understand the type where required;
- no competing source-of-truth semantics remain unresolved.

Validation:
- metamodel activation acceptance checks and related automated tests pass.

Failure behavior:
- type remains `CONCEPT_PROPOSED`;
- production instances MUST NOT be treated as authoritative.

Persistence:
- governance definition and activation evidence; schema/template/tests where applicable.

Audit:
- reason, owner, lifecycle, impacted components, migration decision, verification.

Rollback: deactivate only through an explicit governance transition; existing instances must be migrated, retained as historical/non-authoritative, or retired explicitly.
Migration: REQUIRED assessment; implementation when existing data/artifacts require it.
External effects: depends on affected tooling/workflows.
Human gate: explicit A3 approval required.

### TR-DIAG-CLOSE v1 — Close a diagnostic finding

FROM: `OBSERVED`, `HYPOTHESIS`, or `ROOT_CAUSE_CONFIRMED`
TO: `CLOSED_RESOLVED`, `CLOSED_ACCEPTED_UNKNOWN`, or `CLOSED_NO_ACTION`

Trigger:
- request to close a diagnostic finding.

Preconditions:
- original observation is recorded;
- unsupported hypotheses are not represented as causes;
- root cause is either confirmed or explicitly remains UNKNOWN;
- corrective action is identified when needed;
- preventive/root-cause action is identified when applicable;
- verification of corrective/preventive result exists, or closure explicitly records why residual uncertainty is accepted.

Required authority:
- authority sufficient to accept residual risk/unknowns; higher authority where affected scope requires it.

Required evidence:
- observation/evidence;
- root cause status;
- corrective/preventive action outcome or explicit no-action/accepted-unknown rationale;
- residual risk statement.

Actions:
- classify closure outcome and link follow-up work.

Atomic changes:
- diagnostic status, closure rationale, residual risks/unknowns, follow-up linkage.

Postconditions:
- `CLOSED_RESOLVED`: root cause/correction is verified enough for closure;
- `CLOSED_ACCEPTED_UNKNOWN`: root cause remains UNKNOWN and residual uncertainty is explicitly accepted by sufficient authority;
- `CLOSED_NO_ACTION`: evidence supports that no corrective action is required;
- open follow-up remains tracked separately.

Validation:
- closure category requirements are satisfied.

Failure behavior:
- finding remains open.

Persistence:
- authoritative diagnostic artifact after diagnostic artifact type completes `TR-MODEL-EXTEND`.

Audit:
- observation, hypotheses tested, root-cause status, action, evidence, closure authority.

Rollback: reopen only through explicit diagnostic transition if new evidence invalidates closure.
Migration: existing conversational findings may be migrated when diagnostic model is activated.
External effects: NOT_APPLICABLE unless corrective actions include them.
Human gate: required when accepting material unresolved risk/unknowns beyond agent authority.

## Knowledge ownership principle

Each persistent fact SHOULD have one authoritative owner category. Other files MAY project or summarize that fact but MUST NOT become competing authorities.

Initial ownership:

- `requirements/` owns requirement definitions and approval/status semantics;
- `decisions/` owns decision definitions and approval/status semantics;
- `verification/` is intended to own formal verification/validation results only after that artifact type is activated through `TR-MODEL-EXTEND`;
- `queue/` is intended to own deferred-work records only after that artifact type is activated through `TR-MODEL-EXTEND`;
- task lifecycle ownership remains UNKNOWN and MUST be decided before task transitions become enforceable;
- `state/current.yaml` is a current-state projection and MUST NOT override authoritative facts owned by an activated artifact category.

Projection inconsistency MUST be treated as a consistency defect rather than resolved by arbitrary source selection.

## Migration rule

Promotion of this model does NOT automatically activate existing `VER-*`, `QUEUE-*`, or future diagnostic artifact types. Existing unsupported artifact types MUST undergo `TR-MODEL-EXTEND`, be migrated into an activated model, or be explicitly retired/non-authoritative.

## Acceptance criteria for Transition Model V1

Before promotion to baseline, reviewers MUST verify that:

1. RC-00 is addressed by a generic transition contract rather than local patches.
2. RC-01 is prevented by `TR-MODEL-EXTEND`.
3. RC-02 is addressed by `TR-BASELINE-PROMOTE` and the working/candidate/baseline distinction.
4. Failure paths preserve actual state.
5. H-03 is not silently resolved where evidence is insufficient; task ownership remains explicit UNKNOWN.
6. Governance-significant transition fields are mandatory or explicitly NOT_APPLICABLE.
7. Transition definitions have lifecycle/version semantics.
8. Composed changes have aggregate authority and failure semantics.
9. Non-active artifact types cannot become authoritative.
10. Human approval and baseline promotion are distinct events.
11. Candidate compliance and required tests pass against the candidate to be promoted.
12. Existing Governance V1.0 invariants remain compatible or required changes are explicitly identified.
