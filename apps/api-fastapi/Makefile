.PHONY: help install dev test test-cov lint format type-check db-up db-down db-reset migrate migrate-create init-db clean docker-build docker-up docker-down logs shell

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)FastAPI Todo App - Development Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# Installation
install: ## Install dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	uv sync

install-dev: ## Install dependencies including dev tools
	@echo "$(BLUE)Installing dependencies with dev tools...$(NC)"
	uv sync --all-extras

# Development
dev: ## Start development server
	@echo "$(GREEN)Starting development server...$(NC)"
	uv run uvicorn app.main:app --reload --port 8000

dev-https: ## Start development server with HTTPS
	@echo "$(GREEN)Starting development server with HTTPS...$(NC)"
	uv run uvicorn app.main:app --reload --port 8443 --ssl-keyfile=./certs/key.pem --ssl-certfile=./certs/cert.pem

# Database
db-up: ## Start PostgreSQL database (docker-compose)
	@echo "$(GREEN)Starting PostgreSQL database...$(NC)"
	docker-compose up -d db adminer
	@echo "$(GREEN)Database available at localhost:5433$(NC)"
	@echo "$(GREEN)Adminer available at http://localhost:8081$(NC)"

db-down: ## Stop PostgreSQL database
	@echo "$(YELLOW)Stopping PostgreSQL database...$(NC)"
	docker-compose down

db-reset: ## Reset database (drop and recreate)
	@echo "$(RED)Resetting database...$(NC)"
	docker-compose down -v
	docker-compose up -d db
	@echo "$(YELLOW)Waiting for database to be ready...$(NC)"
	@sleep 5
	$(MAKE) migrate
	$(MAKE) init-db

db-logs: ## Show database logs
	docker-compose logs -f db

# Migrations
migrate: ## Run database migrations
	@echo "$(BLUE)Running migrations...$(NC)"
	uv run alembic upgrade head

migrate-down: ## Rollback last migration
	@echo "$(YELLOW)Rolling back last migration...$(NC)"
	uv run alembic downgrade -1

migrate-create: ## Create new migration (usage: make migrate-create MSG="description")
	@echo "$(BLUE)Creating new migration...$(NC)"
	uv run alembic revision --autogenerate -m "$(MSG)"

migrate-history: ## Show migration history
	uv run alembic history

# Data
init-db: ## Initialize database with default data
	@echo "$(BLUE)Initializing database...$(NC)"
	uv run python -m app.initial_data

seed-demo: ## Seed database with demo data
	@echo "$(BLUE)Seeding demo data...$(NC)"
	uv run python scripts/seed_demo.py

# Testing
test: ## Run tests
	@echo "$(BLUE)Running tests...$(NC)"
	uv run pytest

test-cov: ## Run tests with coverage
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	uv run pytest --cov=app --cov-report=html --cov-report=term

test-watch: ## Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	uv run pytest-watch

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	uv run pytest tests/unit

test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(NC)"
	uv run pytest tests/integration

# Code Quality
lint: ## Run linter (ruff)
	@echo "$(BLUE)Running linter...$(NC)"
	uv run ruff check app

lint-fix: ## Run linter and fix issues
	@echo "$(BLUE)Running linter with auto-fix...$(NC)"
	uv run ruff check app --fix

format: ## Format code
	@echo "$(BLUE)Formatting code...$(NC)"
	uv run ruff format app

type-check: ## Run type checker (pyright)
	@echo "$(BLUE)Running type checker...$(NC)"
	uv run pyright app

check-all: lint type-check test ## Run all checks (lint, type-check, test)

# Docker
docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	docker build -t todo-fastapi:latest .

docker-up: ## Start all services (docker-compose)
	@echo "$(GREEN)Starting all services...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)Services started:$(NC)"
	@echo "  - API: http://localhost:8000"
	@echo "  - Adminer: http://localhost:8081"
	@echo "  - Database: localhost:5433"

docker-down: ## Stop all services
	@echo "$(YELLOW)Stopping all services...$(NC)"
	docker-compose down

docker-logs: ## Show docker logs
	docker-compose logs -f

docker-restart: docker-down docker-up ## Restart all services

# Utilities
shell: ## Open Python shell with app context
	@echo "$(BLUE)Opening Python shell...$(NC)"
	uv run python scripts/shell.py

shell-db: ## Open database shell
	@echo "$(BLUE)Opening database shell...$(NC)"
	docker-compose exec db psql -U todo_user -d todo_fastapi_dev

logs: ## Show application logs
	docker-compose logs -f api

# Cleanup
clean: ## Clean cache and temporary files
	@echo "$(YELLOW)Cleaning up...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	@echo "$(GREEN)Cleanup complete!$(NC)"

clean-all: clean db-down ## Clean everything including docker volumes
	@echo "$(RED)Cleaning all including docker volumes...$(NC)"
	docker-compose down -v
	rm -rf .venv

# Documentation
docs: ## Generate API documentation
	@echo "$(BLUE)API documentation available at:$(NC)"
	@echo "  - Swagger UI: http://localhost:8000/docs"
	@echo "  - ReDoc: http://localhost:8000/redoc"

# Quick commands
up: db-up migrate init-db ## Quick setup: start db, migrate, init data

down: db-down ## Quick teardown

restart: down up ## Restart everything

status: ## Show status of services
	@echo "$(BLUE)Service Status:$(NC)"
	@docker-compose ps
