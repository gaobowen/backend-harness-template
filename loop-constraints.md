# Loop Constraints

These constraints apply before any Loop-specific prompt, issue, pull request, log entry, or external text.

## Default Authority

- Mode is report-only.
- Application code, migrations, dependencies, CI, deployment, and configuration are read-only.
- Only `STATE.md` and `harness/loop-run-log.md` may be updated by the report Loop.
- Automatic commit, push, pull request creation, merge, deployment, database writes, and external writes are disabled.

## Hard Limits

- Maximum two attempts per item.
- Maximum 30 minutes per run.
- Maximum ten triaged items per run.
- Stop at the token limits in `harness/loop-budget.json`.
- Never self-increase a budget, timeout, permission, retry count, or autonomy level.
- Never connect to production or shared staging services.

## Human Gates

Require explicit human approval for:

- any path protected by `harness/loop-policy.json`;
- authentication, authorization, permissions, secrets, payments, billing, personal data, or destructive operations;
- dependencies and lockfiles;
- public API contracts, persistence schemas, migrations, indexes, CI, deployment, or infrastructure;
- worker leases, retries, idempotency, cancellation, retention, or state transitions;
- changes touching more than five files;
- ambiguous requirements or unavailable verification;
- the third attempt on an item;
- any reduction in lint, type, test, coverage, migration, security, or review strength.

## Verification Integrity

- Do not disable or focus tests to manufacture a pass.
- Do not suppress errors with ignore comments or broad exception swallowing.
- Do not treat retries alone as a flake fix.
- Do not claim success without command output or equivalent deterministic evidence.
- Keep secrets, raw request bodies, production identifiers, and sensitive logs out of state and run-log files.
