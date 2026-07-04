# Redash LLM Chatbot — developer commands
# Usage: make help

.DEFAULT_GOAL := help

PYTHON   := .venv/bin/python
PIP      := .venv/bin/pip
PYTEST   := .venv/bin/pytest
RUFF     := .venv/bin/ruff
HYPERCORN := .venv/bin/hypercorn

# Default 5433 on host — macOS/Homebrew Postgres often occupies 5432
POSTGRES_PORT ?= 5433
COMPOSE  := POSTGRES_HOST_PORT=$(POSTGRES_PORT) docker compose -f infra/docker-compose.yml
DB_URL   := postgresql://postgres:postgres@localhost:$(POSTGRES_PORT)/youtube_analytics

.PHONY: help venv install install-backend dev test lint run db-up db-down db-init db-load db-reader db-psql profile-data eda eda-export clean

help: ## Show available targets
	@grep -E '^[a-zA-Z0-9_-]+:.*##' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

venv: ## Create root .venv (idempotent)
	@test -d .venv || python3 -m venv .venv
	@echo "Virtual env ready: .venv/"
	@echo "Activate with: source .venv/bin/activate"

install: venv ## Install backend[dev] + scripts deps into root .venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "Installed. Run: source .venv/bin/activate"

install-backend: venv ## Install only the Quart backend (no ETL deps)
	$(PIP) install --upgrade pip
	$(PIP) install -e "./backend[dev]"

dev: install db-up ## Full local setup: venv + deps + Postgres

test: ## Run backend unit tests
	$(PYTEST) backend/tests scripts/tests -v

lint: ## Ruff check on backend
	$(RUFF) check backend/src backend/tests

run: ## Start Quart API on :8000 (reload)
	$(HYPERCORN) redash_chatbot.app:app --reload --bind 0.0.0.0:8000

db-up: ## Start Postgres via docker-compose
	$(COMPOSE) up -d db
	@echo "Waiting for Postgres..."
	@$(COMPOSE) exec db sh -c 'until pg_isready -U postgres; do sleep 1; done'
	@echo "Postgres ready on localhost:$(POSTGRES_PORT) (DATABASE_URL=$(DB_URL))"

db-down: ## Stop docker-compose services
	$(COMPOSE) down

db-init: ## Apply schema DDL (requires db-up)
	$(COMPOSE) exec -T db psql -U postgres -d youtube_analytics < infra/sql/001_init_schema.sql
	@echo "Schema applied: youtube.*"

db-load: ## Load Data/ CSVs into Postgres (requires db-up, db-init)
	DATABASE_URL=$(DB_URL) $(PYTHON) scripts/load_youtube_data.py --data-dir Data

db-reader: ## Create read-only redash_reader role (Step 2d)
	psql $(DB_URL) -f infra/sql/002_redash_reader.sql

db-psql: ## Open psql shell in the db container
	$(COMPOSE) exec db psql -U postgres -d youtube_analytics

profile-data: ## Profile raw CSVs under Data/
	$(PYTHON) scripts/profile_data.py --output docs/architecture/data-profile.txt

eda: ## Open EDA Jupyter notebook (Task 2c)
	$(PYTHON) -m jupyter notebook notebooks/task-02c-eda-youtube.ipynb

eda-export: ## Export EDA figures + markdown summary (headless)
	DATABASE_URL=$(DB_URL) $(PYTHON) scripts/run_eda.py

clean: ## Remove caches (__pycache__, pytest, ruff); keeps .venv
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

clean-venv: ## Remove root .venv entirely
	rm -rf .venv
