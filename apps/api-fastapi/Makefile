.PHONY: help install dev test test-cov lint format type-check db-up db-down db-reset migrate migrate-create init-db seed-demo  clean docker-build docker-up docker-down logs shell test test-cov

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "FastAPI Todo App - Development Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "%-20s %s\n", $$1, $$2}'

# Installation
install: ## Install dependencies
	@echo "Installing dependencies..."
	uv sync

install-dev: ## Install dependencies including dev tools
	@echo "Installing dependencies with dev tools..."
	uv sync --all-extras

# Development
dev: ## Start development server
	@echo "Starting development server..."
	uv run uvicorn app.main:app --reload --port 8000

dev-https: ## Start development server with HTTPS
	@echo "Starting development server with HTTPS..."
	uv run uvicorn app.main:app --reload --port 8443 --ssl-keyfile=./certs/key.pem --ssl-certfile=./certs/cert.pem

# Database
db-up: ## Start PostgreSQL database (docker-compose)
	@echo "Starting PostgreSQL database..."
	docker-compose up -d db adminer
	@echo "Database available at localhost:5433"
	@echo "Adminer available at http://localhost:8081"

db-down: ## Stop PostgreSQL database and adminer
	@echo "Stopping PostgreSQL database and adminer..."
	docker-compose stop db adminer

db-reset: ## Reset database (destroy and recreate with volumes)
	@echo "Resetting database..."
	docker-compose down -v
	docker-compose up -d db adminer
	@echo "Waiting for database to be ready..."
	@sleep 5
	$(MAKE) migrate
	$(MAKE) init-db

db-logs: ## Show database logs
	docker-compose logs -f db

# Migrations
migrate: ## Run database migrations
	@echo "Running migrations..."
	uv run alembic upgrade head

migrate-down: ## Rollback last migration
	@echo "Rolling back last migration..."
	uv run alembic downgrade -1

migrate-create: ## Create new migration (usage: make migrate-create MSG="description")
	@echo "Creating new migration..."
	uv run alembic revision --autogenerate -m "$(MSG)"

migrate-history: ## Show migration history
	uv run alembic history

# Data
init-db: ## Initialize database with default data
	@echo "Initializing database..."
	uv run python -m app.initial_data

seed-demo: ## Seed database with demo data
	@echo "Seeding demo data..."
	uv run python scripts/seed_demo.py

# Testing
test: ## Run tests
	@echo "Running tests..."
	uv run pytest

test-cov: ## Run tests with coverage
	@echo "Running tests with coverage..."
	uv run pytest --cov=app --cov-report=html --cov-report=term

test-watch: ## Run tests in watch mode
	@echo "Running tests in watch mode..."
	uv run pytest-watch

test-unit: ## Run unit tests only
	@echo "Running unit tests..."
	uv run pytest tests/unit

test-integration: ## Run integration tests only
	@echo "Running integration tests..."
	uv run pytest tests/integration

# Code Quality
lint: ## Run linter (ruff)
	@echo "Running linter..."
	uv run ruff check app

lint-fix: ## Run linter and fix issues
	@echo "Running linter with auto-fix..."
	uv run ruff check app --fix

format: ## Format code
	@echo "Formatting code..."
	uv run ruff format app

type-check: ## Run type checker (pyright)
	@echo "Running type checker..."
	uv run pyright app

check-all: lint type-check test ## Run all checks (lint, type-check, test)

# Docker
docker-build: ## Build Docker image
	@echo "Building Docker image..."
	docker build -t todo-fastapi:latest .

docker-up: ## Start all services (docker-compose)
	@echo "Starting all services..."
	docker-compose up -d
	@echo "Services started:"
	@echo "  - API: http://localhost:8000"
	@echo "  - Adminer: http://localhost:8081"
	@echo "  - Database: localhost:5433"

docker-down: ## Stop all services
	@echo "Stopping all services..."
	docker-compose down

docker-logs: ## Show docker logs
	docker-compose logs -f

docker-restart: docker-down docker-up ## Restart all services

# Utilities
shell: ## Open Python shell with app context
	@echo "Opening Python shell..."
	uv run python scripts/shell.py

shell-db: ## Open database shell
	@echo "Opening database shell..."
	docker-compose exec db psql -U todo_user -d todo_fastapi_dev

logs: ## Show application logs
	docker-compose logs -f api

# Cleanup
clean: ## Clean cache and temporary files
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	@echo "Cleanup complete!"

clean-all: clean db-down ## Clean everything including docker volumes
	@echo "Cleaning all including docker volumes..."
	docker-compose down -v
	rm -rf .venv

# Documentation
docs: ## Generate API documentation
	@echo "API documentation available at:"
	@echo "  - Swagger UI: http://localhost:8000/docs"
	@echo "  - ReDoc: http://localhost:8000/redoc"

# Quick commands
up: db-up migrate init-db ## Quick setup: start db, migrate, init data

down: db-down ## Quick teardown

restart: down up ## Restart everything

status: ## Show status of services
	@echo "Service Status:"
	@docker-compose ps
