SHELL := /bin/bash
COMPOSE := docker compose
TEST_COMPOSE := docker compose -f docker-compose.test.yml -p mulenetx-test
UV := cd backend && uv run

.PHONY: up down logs migrate test test-backend test-frontend test-acceptance test-e2e lint typecheck \
        bench gen-types traceability demo test-services test-services-down

up:
	$(COMPOSE) up --build -d

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f --tail=200

migrate:
	$(COMPOSE) run --rm migrate

# Local test services (PostgreSQL + Neo4j on 127.0.0.1 only; separate project from the app stack).
test-services:
	$(TEST_COMPOSE) up -d --wait

test-services-down:
	$(TEST_COMPOSE) down -v

lint:
	$(UV) ruff check .
	@if [ -f frontend/package.json ]; then cd frontend && npm run lint; fi

typecheck:
	$(UV) mypy mulenetx
	@if [ -f frontend/package.json ]; then cd frontend && npm run typecheck; fi

test: test-backend test-frontend

test-backend: test-services
	$(UV) pytest -m "not docker and not perf and not e2e and not ollama"

test-frontend:
	@if [ -f frontend/package.json ]; then cd frontend && npm test; fi

test-acceptance: test-services
	$(UV) pytest tests/acceptance -m "not docker and not perf"

test-e2e:
	$(UV) pytest tests/e2e -m "e2e"
	@if [ -f frontend/package.json ]; then cd frontend && npm run e2e; fi

bench:
	$(UV) python ../scripts/bench.py

gen-types:
	cd backend && uv run python -m mulenetx.cli export-openapi --out ../docs/openapi.json
	cd frontend && npx openapi-typescript ../docs/openapi.json -o src/api/schema.d.ts

traceability:
	$(UV) python ../scripts/check_traceability.py

demo:
	$(UV) python ../scripts/demo.py
