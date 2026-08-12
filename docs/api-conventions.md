# API Conventions

## Methods

- Use only `GET` and `POST`.
- Use `GET` for safe retrieval without a request body.
- Use `POST` with JSON for search, create, update, save, delete, cancel, retry, and action-style operations.
- Do not add PUT, PATCH, or DELETE routes.

`scripts/check_api_policy.py` mechanically enforces this rule.

## Response Envelope

Successful and failed responses share:

```json
{
  "code": 200,
  "data": {},
  "msg": ""
}
```

Synchronous business errors use the HTTP status in `code` and a stable machine-readable `data.error_code`. Do not make clients parse human text.

## Contracts

- Put public request and response models in `app/schemas`.
- Prefer `extra="forbid"` for state-changing requests.
- Set explicit length, range, collection-size, and enum limits.
- Keep provider-private payloads behind adapters; do not expose them as public contracts.
- Use UTC-aware datetimes and include timezone information in serialized values.
- Commit `docs/openapi.json`; `make openapi-check` blocks accidental contract drift.

## Persistence Boundary

Route modules may receive a database session but may only pass it to `app/db/crud` functions. They must not import SQLAlchemy or call `execute`, `scalar`, `add`, `delete`, `commit`, `rollback`, or `flush`.

Operational probes and provider orchestration belong in dedicated infrastructure helpers or services, not inline route SQL.

## Compatibility

Before changing a public field, status, error code, default, nullability, or endpoint behavior, document:

- existing clients and rollout sequence;
- backward-compatibility window;
- idempotency impact;
- stored-data impact;
- migration and rollback plan;
- updated tests and OpenAPI evidence.
