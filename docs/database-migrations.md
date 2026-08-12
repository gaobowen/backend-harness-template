# Database And Migration Workflow

## Human Gate

Get explicit confirmation before changing a model, migration, table, column, constraint, index, foreign-key action, deletion policy, or schema-affecting CRUD behavior.

Before implementation, align on identity, ownership, time semantics, nullability, uniqueness, concurrency, consistency, idempotency, deletion, retention, backfill, rollout, and rollback.

## Development Workflow

1. Write the intended invariant and compatibility plan.
2. Confirm the schema decision with the responsible developer.
3. Update the SQLAlchemy model.
4. Create a migration; inspect generated SQL and constraint names.
5. Add migration and integration tests for upgrade behavior.
6. Update database and API documentation.
7. Run `make migration-check`.
8. Upgrade a disposable database from an empty state and from the currently deployed revision.
9. Run `make test-integration`.

Do not rely only on Alembic autogeneration. It cannot infer business intent, safe backfills, production lock impact, or rollback semantics.

## Graph Invariants

`scripts/check_migrations.py` requires:

- one migration root;
- one migration head;
- every parent revision to exist;
- unique revision IDs;
- an acyclic graph.

Merge revisions still require human review and a deployment plan.

## Destructive Operations

- Never test destructive migration commands against production or shared staging.
- Resolve the exact database name and environment before cleanup.
- Prefer expand/migrate/contract rollouts for breaking changes.
- Backfills must be bounded, observable, resumable, and safe to retry.
- Downgrade support must be honest; an irreversible migration should say so explicitly rather than pretending data can be reconstructed.

## Example Table

`example_items` is replaceable scaffolding. When removed, replace its initial migration with the adopting project's reviewed baseline instead of retaining meaningless template history.
