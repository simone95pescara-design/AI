# REQ-001 Cold-Start Verification Evidence

Date: 2026-08-08
Requirement: `REQ-001` — Cold-start project reconstructibility
Baseline: Governance V1.0 / `DEC-001`
Method: Cold-start review using only repository contents, without relying on prior conversation context.
Result: PASSED

## Reconstructed project context

Using only repository contents, the reviewer reconstructed the following:

- Project: AI Project Governance Framework.
- Current approved baseline: Governance V1.0, adopted by `DEC-001`.
- Approved cold-start requirement: `REQ-001`.
- Persistent authority and behavioral rules: `AGENTS.md` and the files under `governance/`.
- Current project state before this verification: ACTIVE.
- Open work before this verification: end-to-end cold-start validation of `REQ-001`.
- Current task before this verification: `TASK-001`, DOING, verification PARTIAL.
- Next action before this verification: execute the cold-start review and record the result against the `REQ-001` acceptance criteria.

## Acceptance criteria

1. **A cold-start agent identifies Governance V1.0 as the current approved baseline — PASS.**
   Evidence: `state/current.yaml` identifies `Governance V1.0 / DEC-001`; `decisions/DEC-001.yaml` records the baseline adoption as APPROVED.

2. **A cold-start agent identifies DEC-001 and REQ-001 — PASS.**
   Evidence: `decisions/DEC-001.yaml` and `requirements/REQ-001.yaml` are explicit persistent records with APPROVED status.

3. **A cold-start agent can state the current project status and next action from state/current.yaml — PASS.**
   Evidence: before this verification, `state/current.yaml` stated status ACTIVE, `TASK-001` DOING, verification PARTIAL, and explicitly listed the cold-start review and evidence recording as next actions.

4. **The agent can distinguish normative repository information from temporary conversation context — PASS.**
   Evidence: `AGENTS.md` states that the repository is persistent and authoritative project memory while conversations are temporary working memory; `governance/SPECIFICATION.md` repeats this under KNO-001 and requires significant confirmed information to be persisted under KNO-002.

## Conclusion

All `REQ-001` acceptance criteria were satisfied using repository contents alone. No prior chat history was required to reconstruct the baseline, authoritative rules, approved decision and requirement, current state, open work, or next action.

Verification status: PASSED
Task outcome: `TASK-001` may be marked DONE with verification PASSED.
