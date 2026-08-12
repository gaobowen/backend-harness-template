# Harness Adoption Guide

## Phase 1: Context

- Replace the sample project context and architecture.
- Remove the example feature and document real module boundaries.
- Encode durable failure lessons in `AGENTS.md`.
- Define public API, persistence, provider, worker, and Git workflows.

Exit when a new engineer or Agent can locate the correct module, invariant, owner, and verification path without oral history.

## Phase 2: Deterministic Harness

- Replace sample tests with business-critical unit, contract, migration, and integration coverage.
- Require CI and human review on the default branch.
- Add project-specific protected paths and mechanical checks.
- Commit and verify OpenAPI.
- Add observability for important requests, tasks, provider calls, retries, and terminal states.

Exit when a normal backend change can be accepted or rejected using reproducible evidence rather than reviewer intuition alone.

## Phase 3: Report-Only Loop

- Schedule narrow triage at a low cadence.
- Read `STATE.md` at the beginning and update it at the end.
- Record budget, findings, sanitized evidence, and escalation.
- Do not edit application code or perform Git, database, provider, deployment, or external writes.
- Review every report for at least two weeks.

Exit when reports are useful, low-noise, and do not repeatedly misclassify backend risk.

## Phase 4: Assisted Fixes

- Allow only small, allowlisted changes in isolated worktrees.
- Use separate Builder and Checker contexts.
- Require green CI and a human-reviewed draft PR or MR.
- Stop after two failed attempts.
- Keep dependencies, auth, API, database, worker state machines, CI, deployment, and infrastructure protected.

Exit after at least four stable weeks with a human rejection rate below 10%, no escaped high-risk changes, and cost within budget.

## Phase 5: Unattended Work

Enable only for low-risk repetitive work with reliable validators, strict budgets, an explicit kill switch, and an auto-merge path allowlist. Unattended behavior is a project-specific policy decision, never a template default.
