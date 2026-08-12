# Testing Strategy

## Layers

1. Unit tests for validation, permissions, normalization, pricing, error mapping, and state-transition decisions.
2. Route tests with dependency or adapter substitution for deterministic HTTP contracts.
3. Integration tests against isolated PostgreSQL and Redis services.
4. Provider contract tests using sanitized fixtures, never live production credentials.
5. Worker tests for leasing, heartbeat, retry, idempotent finalization, expiration, and crash recovery.

## Determinism

- Freeze time and IDs when assertions depend on them.
- Use sanitized fixtures for provider and stored-document payloads.
- Mock external HTTP, object storage, email, and payment services in CI.
- Never require production or shared staging to make CI green.
- Do not solve flakes by blindly increasing retries, sleeps, or timeouts.
- Tests that modify data must use an explicitly disposable database.

## Regression Rule

For a deterministic bug:

1. Add a test that fails for the reported behavior.
2. Implement the smallest fix.
3. Show the focused test and affected suite passing.
4. Add a mechanical Harness rule when the failure represents a durable project-wide invariant.

If a regression test is impractical, explain the missing verification and residual risk in the pull request or merge request.

## Coverage

The starter requires 80% branch-aware coverage for configured application code. Harness scripts are verified by direct execution in `preflight`. Replace sample coverage with business-critical assertions before raising autonomy. Lowering thresholds requires explicit approval and a written reason.

## Commands

```bash
make test-unit
make test-coverage
APP_ENV_FILE=.env.test make db-upgrade test-integration
make security-audit
make verify
```
