# Example API

The example API exists to prove Harness behavior. Replace it with product contracts during adoption.

## Health

- `GET /api/health/live`: process liveness only.
- `GET /api/health/ready`: verifies PostgreSQL and Redis connectivity.

## Example Items

- `POST /api/examples/create`
- `POST /api/examples/get`
- `POST /api/examples/search`

State-changing request models reject unknown fields. All responses use the common envelope documented in `docs/api-conventions.md`.

The generated machine-readable contract is committed as `docs/openapi.json` and verified by `make openapi-check`.
