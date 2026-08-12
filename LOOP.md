# Daily Backend Triage Loop

## Goal

Find reproducible repository-health problems, record concise evidence, and escalate actionable backend work without modifying application code or external systems.

## Non-Goals

- Do not implement fixes in report-only mode.
- Do not change dependencies, API contracts, auth, database schema, migrations, worker state machines, CI, deployment, or infrastructure.
- Do not commit, push, open or merge pull requests or merge requests, deploy, call provider APIs, or write to databases, caches, object storage, or ticketing systems.
- Do not weaken tests, coverage, lint, types, schema checks, migration checks, or Harness policy.

## Trigger

Run manually, once per day, or after a CI failure. Do not use a cadence shorter than two hours for the default pattern.

## Inputs

Read in order:

1. `AGENTS.md`
2. `docs/project-context.md`
3. `docs/architecture.md`
4. `STATE.md`
5. `loop-constraints.md`
6. `harness/loop-policy.json`
7. `harness/loop-budget.json`
8. The current branch, working-tree status, recent CI evidence, and relevant source changes

## Run

1. Confirm the policy still says `report-only`.
2. Refuse to continue when working-tree ownership or overlapping changes are ambiguous.
3. Read unresolved items from `STATE.md`; remove only items proven resolved.
4. Run `make preflight`.
5. Run `make security-audit` only when the locked environment is available.
6. Run integration tests only against an explicitly isolated test database and Redis database.
7. Classify findings as reproducible failure, flaky or insufficient evidence, protected or high-risk, or resolved.
8. Update only `STATE.md` and `harness/loop-run-log.md` with evidence and the next human action.
9. Stop when there are no actionable findings or any budget, time, attempt, ambiguity, service-isolation, or protected-path boundary is reached.

## Evidence Standard

Every finding must include:

- exact failing command;
- relevant file or subsystem;
- minimal sanitized error summary;
- reproducibility status;
- risk classification;
- affected API, data, worker, or deployment boundary;
- recommended next human action.

## Escalation

Escalate immediately for protected paths, dependency changes, missing acceptance criteria, security or privacy concerns, data compatibility, idempotency, time semantics, deployment, unavailable isolated services, a third attempt, or any proposed reduction in verification strength.

## Done When

- Supported checks and evidence collection are complete.
- `STATE.md` reflects current unresolved work without duplicates.
- The run log contains one concise entry.
- No application, configuration, dependency, Git, database, deployment, or external-system write occurred.
