# BOOTSTRAP.md

## Purpose

This file defines the deterministic entry sequence for any new AI agent or conversation joining the project.

The repository must be sufficient to reconstruct operational context without access to previous conversations.

## Boot sequence

Before performing significant project work, the agent MUST:

1. Read `AGENTS.md`.
2. Read `governance/SPECIFICATION.md` and `governance/transition-model.md` when needed to resolve normative detail, authority, ambiguity, conflict, or state transitions.
3. Read `state/current.yaml` to establish the current project baseline and discover active operational artifact IDs.
4. Read active approved requirements under `requirements/` relevant to the current task.
5. Read active approved decisions under `decisions/` relevant to the current task.
6. For IDs projected by state, read the authoritative owner artifacts:
   - `tasks/TASK-*.yaml` for executable task lifecycle;
   - `queue/QUEUE-*.yaml` for deliberately deferred work;
   - `diagnostics/DIA-*.yaml` for open diagnostics/root-cause work;
   - `verification/VER-*.yaml` for verification/validation evidence linked by relevant tasks or requirements.
7. Identify any additional governance policy applicable to the requested work.
8. Check for contradictions between projections and authoritative owner artifacts, stale information, unresolved blockers, and missing critical context.
9. Establish the baseline on which the work will be performed.
10. Only then begin significant execution.

Until `DEC-003` is approved and promoted, the operational artifact ownership in step 6 is candidate behavior and existing VER/QUEUE/TASK/DIA artifacts MUST NOT be treated as authoritative solely because they exist on a candidate branch.

## Bootstrap assessment

When explicitly asked to confirm bootstrap, the agent SHOULD report concisely:

- current baseline;
- current status;
- relevant approved requirements;
- relevant approved decisions;
- active task IDs and blockers;
- open diagnostic IDs;
- queued work IDs;
- relevant verification evidence;
- conflicts/stale projections;
- next action.

The agent MUST NOT claim to have read or verified repository information it did not actually access.

## Standard external bootstrap instruction

The minimum recommended instruction for a new conversation is:

> Project: <repository URL>. Bootstrap the project according to the repository instructions and operate according to its governance. Before acting, confirm the current baseline, status, and next action.

The external instruction is only an entry pointer. Governance and project knowledge remain in the repository.

## Failure to access the repository

If the agent cannot access the repository or required authoritative files, it MUST say so and MUST NOT pretend that bootstrap succeeded.
