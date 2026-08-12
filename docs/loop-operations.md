# Loop Operations

## Default Mode

The template starts in `report-only`. A scheduler is intentionally not installed because cadence, credentials, repository permissions, service isolation, and notifications belong to the adopting team.

## Suggested First Trigger

Run daily or after failed CI:

```text
Follow LOOP.md in report-only mode. Read STATE.md and machine-readable policy first. Run supported deterministic checks, record sanitized evidence, stop at budget or escalation boundaries, and do not modify application code or perform Git, database, deployment, provider, or external-system writes.
```

## Promotion To Assisted Mode

All conditions are required:

- CI is a required branch-protection check.
- Critical API and persistence behavior has deterministic tests.
- High-risk paths are complete and mechanically checked.
- Builder and Checker use separate contexts.
- Changes use isolated worktrees.
- Git permissions are minimal; production credentials are unavailable.
- Maximum attempts, files, duration, and token budget are enforced.
- A human explicitly edits the autonomy policy.

## Kill Conditions

Pause the Loop when:

- two consecutive runs fail;
- the same item reaches two failed attempts;
- a protected path is implicated;
- acceptance criteria are ambiguous;
- state and source evidence disagree;
- an isolated test service cannot be proven safe;
- budget or maximum duration is reached;
- verification becomes flaky;
- the Loop proposes weakening a gate.

## Incident Handling

1. Disable scheduling and revoke write credentials.
2. Preserve the patch and sanitized evidence.
3. Revert bad changes through the normal reviewed process.
4. Assess API, data, provider, billing, and deployment impact.
5. Record the failure mode in `STATE.md` and the run log.
6. Add or strengthen a deterministic gate before resuming.
