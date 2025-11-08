# Makefile Usage Guide

## Overview

The Flask API includes a comprehensive Makefile that simplifies common development tasks. This is the recommended way to run and manage the application.

## Quick Reference

### Essential Commands

```bash
# First time setup
make quickstart          # Install deps + initialize DB with test data

# Development
make run-dev             # Start dev server with auto-reload (recommended)
make run                 # Start production server
make stop                # Stop running server

# Database
make db-init             # Create database tables
make db-reinit           # Reset database with demo users/todos
make db-drop             # Drop all tables (with confirmation)

# Testing
make test                # Run all tests
make test-cov            # Run tests with coverage report

# Utilities
make health              # Check if API is healthy
make docs                # Show API documentation URLs
make clean               # Clean up generated files
make help                # Show all available commands
```

## Detailed Command Reference

### Setup & Dependencies

```bash
make install             # Install production dependencies
make dev                 # Install all dependencies (including dev)
make clean               # Remove __pycache__, .pyc files, test artifacts
```

### Running the Server

```bash
# Development mode (auto-reload on file changes)
make run-dev
# Starts on: http://localhost:5000
# Uses Flask's development server with --reload flag

# Production mode (standard)
make run
# Uses: uv run python main.py

# Production mode (Gunicorn - recommended for production)
make run-prod
# Uses: gunicorn with 4 workers

# Custom port
FLASK_PORT=8080 make run-dev
```

### Database Management

```bash
# Initialize database (first time)
make db-init
# Creates all tables using SQLAlchemy models

# Reinitialize with test data
make db-reinit
# - Clears all existing data
# - Creates demo users based on DEMO_USERS env var
# - Creates 3 todos per user
# Demo accounts: guest1@zatvia.com, admin1@zatvia.com, sysadmin1@zatvia.com
# Default password: Todo#### (from DEMO_PASSWORD env var)

# Drop all tables
make db-drop
# Asks for confirmation before dropping
```

### Testing & Quality

```bash
# Run tests
make test
# Runs pytest on tests/ directory

# Run tests with coverage
make test-cov
# Generates HTML coverage report in htmlcov/
# Shows coverage percentage in terminal

# Run tests in watch mode (if pytest-watch is installed)
make test-watch

# Linting (requires ruff)
make lint
# Checks code style and potential issues

# Format code (requires ruff)
make format
# Auto-formats Python files
```

### Health Checks

```bash
# Check API health
make health
# Calls: GET http://localhost:5000/health

# Check API readiness (includes DB connectivity)
make readiness
# Calls: GET http://localhost:5000/readiness
```

### Management Script Shortcuts

```bash
# Register new user
make register EMAIL=test@example.com PASSWORD=pass123 NAME="Test User"

# Login
make login EMAIL=test@example.com PASSWORD=pass123
# Saves tokens to .dev-tokens.json

# Get user profile
make profile

# List todos
make todos-list
```

### Documentation

```bash
# Show API documentation URLs
make docs
# Displays:
# - Swagger UI: http://localhost:5000/docs
# - ReDoc: http://localhost:5000/redoc
# - OpenAPI Spec: http://localhost:5000/api-spec
```

### Workflow Commands

```bash
# Complete development setup
make dev-setup
# Runs: install dev dependencies + db-reinit

# Quick restart
make restart
# Stops current server and starts a new one

# Clean start
make all
# Runs: clean + install + test

# Stop server
make stop
# Kills all running Flask processes
```

## Common Workflows

### First Time Setup

```bash
cd apps/api-flask
make quickstart
# This will:
# 1. Install all dependencies
# 2. Initialize database
# 3. Create demo users and todos
# 4. Show next steps
```

### Daily Development

```bash
# Start your day
make run-dev

# In another terminal, test changes
make health
make test

# When done
make stop
```

### Testing Workflow

```bash
# Make code changes...

# Run tests
make test

# Check coverage
make test-cov

# View coverage report
open htmlcov/index.html
```

### Database Reset

```bash
# Reset database to clean state with demo data
make db-reinit

# Login as demo user
make login EMAIL=admin1@zatvia.com PASSWORD='Todo####'

# List todos
make todos-list
```

### Production Deployment

```bash
# Install production dependencies only
make install

# Initialize database
make db-init

# Run with Gunicorn
make run-prod
```

## Environment Variables

The Makefile respects these environment variables:

```bash
# Port configuration
FLASK_PORT=8080 make run-dev

# Environment
FLASK_ENV=production make run

# All environment variables from .env are automatically loaded
```

## Comparison with uv Commands

| Makefile | uv Equivalent |
|----------|---------------|
| `make install` | `uv sync` |
| `make run-dev` | `uv run flask --app main.py run --reload` |
| `make run` | `uv run python main.py` |
| `make test` | `uv run pytest tests/` |
| `make db-reinit` | `uv run python scripts/manage.py db reinit` |

The Makefile provides convenient shortcuts and better defaults.

## Customization

You can override Makefile variables:

```bash
# Use different Python command
PYTHON="python3.12" make test

# Use different port
FLASK_PORT=8000 make run-dev

# Change Flask app
FLASK_APP=app.py make run
```

## Troubleshooting

### Command Not Found

Make sure you're in the `apps/api-flask` directory:
```bash
cd apps/api-flask
make help
```

### Port Already in Use

```bash
# Stop existing server
make stop

# Or manually
lsof -i :5000
kill -9 <PID>
```

### Database Errors

```bash
# Check if PostgreSQL is running
psql -U todo_user -d todo_nestjs_dev -h localhost

# Verify DATABASE_URL in .env
cat ../../.env | grep DATABASE_URL

# Reset database
make db-drop
make db-init
```

### Permission Errors

Make sure the Makefile is in the correct location:
```bash
ls -la Makefile
# Should show: -rw-r--r--  1 user  staff  ... Makefile
```

## Tips

1. **Always use `make run-dev` for development** - it provides auto-reload
2. **Run `make quickstart` on first setup** - it does everything you need
3. **Use `make help` to see all commands** - the list is comprehensive
4. **Check health before testing** - `make health` confirms API is running
5. **Use `make db-reinit` frequently** - gives you a clean slate with test data

## See Also

- [RUNNING.md](./RUNNING.md) - Complete guide to running the server
- [scripts/README.md](./scripts/README.md) - Management script documentation
- [README.md](./README.md) - Main project documentation
