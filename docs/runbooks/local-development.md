# Local Development Runbook

## Bootstrap

```bash
uv sync --all-groups
cp .env.example .env
cp .env.test.example .env.test
docker compose up -d
APP_ENV_FILE=.env.test uv run alembic upgrade head
```

## Run The API

```bash
uv run uvicorn app.main:app --reload --port 8080
```

## Verify

```bash
make preflight
APP_ENV_FILE=.env.test make security-audit db-upgrade test-integration
```

## Stop Services

```bash
docker compose stop
```

Deleting volumes removes local data and is intentionally not included as a routine command. Resolve and confirm the exact disposable project before performing cleanup.
