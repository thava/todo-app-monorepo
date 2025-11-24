# Flask API Management Scripts

This directory contains management scripts for the Flask API backend.

## manage.py

A comprehensive CLI utility for managing the Flask API, closely modeled after `apps/api-nestjs/scripts/utils.ts`.

### Prerequisites

Ensure all dependencies are installed:

```bash
cd apps/api-flask
uv sync
```

### Usage

All commands should be run from the `apps/api-flask` directory:

```bash
python scripts/manage.py [COMMAND] [OPTIONS]
```

### Configuration

The script automatically loads environment variables from the root `.env` file:
- `FLASK_PORT`: Default 5000 : URL `http://localhost:5000`
- `DEMO_DOMAIN`: Domain for demo users (default: `mydomain.com`)
- `DEMO_PASSWORD`: Password for demo users (default: `mypassword`)
- `DEMO_USERS`: Comma-separated list of demo users (default: `guest1,admin1,sysadmin1`)

Tokens are saved to `.dev-tokens.json` in the current working directory.

## Available Commands

### Database Management

```bash
# Initialize database tables
python scripts/manage.py db init

# Drop all database tables
python scripts/manage.py db drop

# Reinitialize database with test data (clears all data and creates demo users/todos)
python scripts/manage.py db reinit
```

The `db:reinit` command:
- Clears all existing data
- Creates test users based on `DEMO_USERS` environment variable
- Each user gets 3 sample todos
- User roles are inferred from username prefix (guest*, admin*, sysadmin*)

### Authentication

```bash
# Register a new user
python scripts/manage.py register test@example.com password123 "Test User"

# Login and save tokens
python scripts/manage.py login test@example.com password123

# Refresh access token
python scripts/manage.py refresh

# Logout and clear tokens
python scripts/manage.py logout

# Get current user profile
python scripts/manage.py profile
```

### Todo Operations

```bash
# Create a new todo
python scripts/manage.py todos create "Buy groceries" --priority=high --due="2025-12-31"

# List all todos
python scripts/manage.py todos list

# Get a specific todo
python scripts/manage.py todos get <todo_id>

# Update a todo
python scripts/manage.py todos update <todo_id> --description="New description" --priority=low

# Delete a todo
python scripts/manage.py todos delete <todo_id>
```

### Admin User Management

Requires admin or sysadmin role.

```bash
# List all users
python scripts/manage.py admin users

# Get a specific user
python scripts/manage.py admin users:get <user_id>

# Update user (sysadmin only)
python scripts/manage.py admin users:update <user_id> --role=admin --email-verified-at=now

# Delete user (sysadmin only)
python scripts/manage.py admin users:delete <user_id>
```

Update options:
- `--email`: New email address
- `--password`: New password
- `--full-name`: New full name
- `--role`: New role (guest, admin, sysadmin)
- `--email-verified-at`: Email verified timestamp (empty string, "null", "now", or ISO date)

### Health Checks

```bash
# Check API health
python scripts/manage.py health

# Check API readiness
python scripts/manage.py readiness
```

### Token Management

```bash
# Clear saved tokens
python scripts/manage.py tokens clear
```

## Examples

### Quick Start Workflow

```bash
# 1. Initialize database with demo data
python scripts/manage.py db reinit

# 2. Login as demo user
python scripts/manage.py login admin1@zatvia.com "Todo####"

# 3. List todos
python scripts/manage.py todos list

# 4. Create a new todo
python scripts/manage.py todos create "Complete documentation" --priority=high

# 5. Get user profile
python scripts/manage.py profile

# 6. List all users (admin only)
python scripts/manage.py admin users
```

### Development Workflow

```bash
# Drop and recreate database with fresh test data
python scripts/manage.py db drop
python scripts/manage.py db init
python scripts/manage.py db reinit

# Test authentication flow
python scripts/manage.py register dev@example.com devpass123 "Dev User"
python scripts/manage.py login dev@example.com devpass123
python scripts/manage.py profile
python scripts/manage.py logout
```

## Comparison with NestJS utils.ts

This script provides feature parity with `apps/api-nestjs/scripts/utils.ts`:

| Feature | NestJS (utils.ts) | Flask (manage.py) |
|---------|-------------------|-------------------|
| Database reinit | ✅ | ✅ |
| User registration | ✅ | ✅ |
| Login/logout | ✅ | ✅ |
| Token refresh | ✅ | ✅ |
| Profile management | ✅ | ✅ |
| Todo CRUD | ✅ | ✅ |
| Admin user management | ✅ | ✅ |
| Health checks | ✅ | ✅ |
| Token file management | ✅ | ✅ |
| Color-coded output | ✅ | ✅ |
| JSON formatting | ✅ | ✅ |

## Notes

- The script uses SQLAlchemy models that are compatible with the Drizzle schema in `packages/database/src/schema/`
- Database initialization via `db init` uses SQLAlchemy's `db.create_all()` which creates tables based on the models
- The `db:reinit` command provides the same test data structure as the NestJS version
- All API requests use the same endpoints as NestJS, ensuring compatibility
