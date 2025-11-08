.PHONY: help install dev test test-cov clean db-init db-drop db-reinit run run-dev run-prod docs lint format health

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Configuration
PYTHON := uv run python
FLASK_APP := main.py
FLASK_PORT ?= 5000

help: ## Show this help message
	@echo "$(BLUE)Flask API - Available Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Setup & Dependencies:$(NC)"
	@grep -E '^(install|dev|clean):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Development:$(NC)"
	@grep -E '^(run|run-dev|run-prod|docs):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Database:$(NC)"
	@grep -E '^(db-init|db-drop|db-reinit):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Testing & Quality:$(NC)"
	@grep -E '^(test|test-cov|lint|format):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Health Checks:$(NC)"
	@grep -E '^(health|readiness):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(BLUE)Examples:$(NC)"
	@echo "  make install      # Install dependencies"
	@echo "  make db-reinit    # Initialize database with test data"
	@echo "  make run-dev      # Run development server"
	@echo "  make test         # Run tests"

install: ## Install dependencies
	@echo "$(GREEN)Installing dependencies...$(NC)"
	uv sync

dev: install ## Install dependencies including dev dependencies
	@echo "$(GREEN)Installing dev dependencies...$(NC)"
	uv sync --all-extras

clean: ## Clean up generated files
	@echo "$(YELLOW)Cleaning up...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -f .coverage
	rm -rf htmlcov/
	rm -f .dev-tokens.json
	@echo "$(GREEN)Clean complete!$(NC)"

# Database commands
db-init: ## Initialize database tables
	@echo "$(GREEN)Initializing database...$(NC)"
	$(PYTHON) scripts/manage.py db init

db-drop: ## Drop all database tables
	@echo "$(RED)Dropping all database tables...$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(PYTHON) scripts/manage.py db drop; \
	else \
		echo "Aborted."; \
	fi

db-reinit: ## Reinitialize database with test data
	@echo "$(GREEN)Reinitializing database with test data...$(NC)"
	$(PYTHON) scripts/manage.py db reinit

# Run commands
run: ## Run the Flask server (production mode)
	@echo "$(GREEN)Starting Flask server on port $(FLASK_PORT)...$(NC)"
	$(PYTHON) $(FLASK_APP)

run-dev: ## Run the Flask server in development mode with auto-reload
	@echo "$(GREEN)Starting Flask development server on port $(FLASK_PORT)...$(NC)"
	@export FLASK_ENV=development && \
	export FLASK_DEBUG=1 && \
	uv run flask --app $(FLASK_APP) run --host=0.0.0.0 --port=$(FLASK_PORT) --reload

run-prod: ## Run the Flask server in production mode with gunicorn
	@echo "$(GREEN)Starting Flask production server with gunicorn...$(NC)"
	@if ! command -v gunicorn &> /dev/null; then \
		echo "$(RED)Gunicorn not installed. Installing...$(NC)"; \
		uv pip install gunicorn; \
	fi
	uv run gunicorn -w 4 -b 0.0.0.0:$(FLASK_PORT) "main:app"

# Testing
test: ## Run tests
	@echo "$(GREEN)Running tests...$(NC)"
	$(PYTHON) -m pytest tests/ -v

test-cov: ## Run tests with coverage report
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	$(PYTHON) -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term

test-watch: ## Run tests in watch mode
	@echo "$(GREEN)Running tests in watch mode...$(NC)"
	$(PYTHON) -m pytest tests/ -v --watch

# Code quality
lint: ## Run linting checks
	@echo "$(GREEN)Running linting checks...$(NC)"
	@if command -v ruff &> /dev/null; then \
		uv run ruff check src/ tests/; \
	else \
		echo "$(YELLOW)Ruff not installed. Install with: uv pip install ruff$(NC)"; \
	fi

format: ## Format code
	@echo "$(GREEN)Formatting code...$(NC)"
	@if command -v ruff &> /dev/null; then \
		uv run ruff format src/ tests/ scripts/; \
	else \
		echo "$(YELLOW)Ruff not installed. Install with: uv pip install ruff$(NC)"; \
	fi

# Documentation
docs: ## Open API documentation in browser
	@echo "$(BLUE)API Documentation available at:$(NC)"
	@echo "  Swagger UI:  http://localhost:$(FLASK_PORT)/docs"
	@echo "  ReDoc:       http://localhost:$(FLASK_PORT)/redoc"
	@echo "  OpenAPI:     http://localhost:$(FLASK_PORT)/api-spec"

# Health checks
health: ## Check API health
	@echo "$(GREEN)Checking API health...$(NC)"
	@curl -s http://localhost:$(FLASK_PORT)/health | python -m json.tool || echo "$(RED)API is not running$(NC)"

readiness: ## Check API readiness
	@echo "$(GREEN)Checking API readiness...$(NC)"
	@curl -s http://localhost:$(FLASK_PORT)/readiness | python -m json.tool || echo "$(RED)API is not running$(NC)"

# Management commands shortcuts
register: ## Register a new user (usage: make register EMAIL=test@example.com PASSWORD=pass123 NAME="Test User")
	@if [ -z "$(EMAIL)" ] || [ -z "$(PASSWORD)" ] || [ -z "$(NAME)" ]; then \
		echo "$(RED)Usage: make register EMAIL=test@example.com PASSWORD=pass123 NAME=\"Test User\"$(NC)"; \
		exit 1; \
	fi
	$(PYTHON) scripts/manage.py register $(EMAIL) $(PASSWORD) "$(NAME)"

login: ## Login (usage: make login EMAIL=test@example.com PASSWORD=pass123)
	@if [ -z "$(EMAIL)" ] || [ -z "$(PASSWORD)" ]; then \
		echo "$(RED)Usage: make login EMAIL=test@example.com PASSWORD=pass123$(NC)"; \
		exit 1; \
	fi
	$(PYTHON) scripts/manage.py login $(EMAIL) $(PASSWORD)

profile: ## Get current user profile
	$(PYTHON) scripts/manage.py profile

todos-list: ## List all todos
	$(PYTHON) scripts/manage.py todos list

# Quick start workflow
quickstart: install db-reinit ## Quick start: install deps and initialize database
	@echo "$(GREEN)✓ Setup complete!$(NC)"
	@echo ""
	@echo "$(BLUE)Next steps:$(NC)"
	@echo "  1. Start the server:    make run-dev"
	@echo "  2. View API docs:       http://localhost:$(FLASK_PORT)/docs"
	@echo "  3. Login as demo user:  make login EMAIL=admin1@zatvia.com PASSWORD='Todo####'"
	@echo "  4. List todos:          make todos-list"

# Development workflow
dev-setup: dev db-reinit ## Complete development setup
	@echo "$(GREEN)✓ Development environment ready!$(NC)"
	@echo ""
	@echo "Run 'make run-dev' to start the development server"

# All-in-one commands
all: clean install test ## Clean, install, and test

restart: ## Restart the development server
	@echo "$(YELLOW)Restarting server...$(NC)"
	@pkill -f "flask run" || true
	@sleep 1
	@make run-dev

stop: ## Stop the running server
	@echo "$(YELLOW)Stopping server...$(NC)"
	@pkill -f "flask run" || pkill -f "python main.py" || echo "No server running"
