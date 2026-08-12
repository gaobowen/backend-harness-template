UV ?= uv
PYTHON ?= $(UV) run python

.PHONY: help sync format format-check lint typecheck test-unit test-coverage test-integration \
	check-harness check-api-policy check-db-boundaries migration-check db-upgrade \
	security-audit import-check openapi-generate openapi-check preflight verify harness-create harness-init

help:
	@echo "sync                 Install locked runtime and development dependencies"
	@echo "preflight            Run deterministic local quality gates"
	@echo "verify               Run the complete gate, including services-backed tests"
	@echo "harness-create       Copy and initialize a new project; pass ARGS='...'"
	@echo "harness-init         Reinitialize this copy; pass ARGS='...'"

sync:
	$(UV) sync --all-groups

format:
	$(UV) run ruff format .
	$(UV) run ruff check . --fix

format-check:
	$(UV) run ruff format --check .

lint:
	$(UV) run ruff check .

typecheck:
	$(UV) run mypy app scripts

test-unit:
	$(UV) run pytest -m "not integration" tests/unit

test-coverage:
	$(UV) run pytest -m "not integration" tests/unit --cov=app --cov-report=term-missing --cov-report=xml

test-integration:
	$(UV) run pytest -m integration tests/integration

check-harness:
	$(PYTHON) scripts/check_harness.py

check-api-policy:
	$(PYTHON) scripts/check_api_policy.py

check-db-boundaries:
	$(PYTHON) scripts/check_db_boundaries.py

migration-check:
	$(PYTHON) scripts/check_migrations.py

db-upgrade:
	$(UV) run alembic upgrade head

security-audit:
	$(UV) run pip-audit

import-check:
	$(UV) run python -c "from app.main import app; assert app.title"

openapi-generate:
	$(UV) run python scripts/check_openapi.py --write

openapi-check:
	$(UV) run python scripts/check_openapi.py --check

preflight: format-check lint typecheck test-coverage check-harness check-api-policy check-db-boundaries migration-check import-check openapi-check

verify: preflight security-audit db-upgrade test-integration

harness-create:
	$(PYTHON) scripts/create_project.py $(ARGS)

harness-init:
	$(PYTHON) scripts/init_harness.py $(ARGS)
