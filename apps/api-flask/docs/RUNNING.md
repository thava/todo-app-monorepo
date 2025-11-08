# Running the Flask API

Quick reference guide for starting and managing the Flask API server.

## Quick Start (30 seconds)

```bash
cd apps/api-flask
make quickstart
make run-dev
```

The API will be running at `http://localhost:5000`

## Methods to Run the Server

### 1. Using Makefile (Recommended)

**Development mode with auto-reload:**
```bash
make run-dev
```

**Production mode:**
```bash
make run
```

**Production with Gunicorn (recommended for production):**
```bash
make run-prod
```

### 2. Using uv Command

**Simple run:**
```bash
uv run python main.py
```

**With Flask's development server (auto-reload):**
```bash
uv run flask --app main.py run --host=0.0.0.0 --port=5000 --reload
```

**Set environment variables:**
```bash
FLASK_PORT=5001 uv run python main.py
```

### 3. Using Shell Script

```bash
./run.sh
```

### 4. Traditional Python (after activating venv)

```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python main.py
```

## Configuration

The server respects these environment variables:

- `FLASK_PORT` - Port to run on (default: 5000)
- `FLASK_ENV` - Environment (development/production)
- `FLASK_DEBUG` - Enable debug mode (0/1)
- `DATABASE_URL` - PostgreSQL connection string
- `FLASKAPI_URL` - Base URL for the API

These are read from the root `.env` file or can be set directly:

```bash
FLASK_PORT=8080 make run-dev
```

## Database Setup

### First Time Setup

```bash
# Initialize database tables
make db-init
```

### Reset Database with Test Data

```bash
# Drops all data and creates demo users + todos
make db-reinit
```

This creates test accounts:
- `guest1@zatvia.com` - Guest user
- `admin1@zatvia.com` - Admin user
- `sysadmin1@zatvia.com` - System admin user

All with password: `Todo####`

### Manual Database Operations

```bash
# Drop all tables
make db-drop

# Initialize tables
make db-init
```

## API Documentation

Once the server is running:

- **Swagger UI**: http://localhost:5000/docs
- **ReDoc**: http://localhost:5000/redoc
- **OpenAPI Spec**: http://localhost:5000/api-spec

Or use:
```bash
make docs  # Shows documentation URLs
```

## Health Checks

```bash
# Check if API is healthy
make health

# Check if API is ready (includes DB connectivity)
make readiness
```

Or access directly:
- http://localhost:5000/health
- http://localhost:5000/readiness

## Testing the API

### Using the Management Script

```bash
# Login as demo user
python scripts/manage.py login admin1@zatvia.com "Todo####"

# List todos
python scripts/manage.py todos list

# Create a todo
python scripts/manage.py todos create "Test todo" --priority=high
```

### Using Make Commands

```bash
# Login
make login EMAIL=admin1@zatvia.com PASSWORD='Todo####'

# List todos
make todos-list

# View profile
make profile
```

### Using curl

```bash
# Health check
curl http://localhost:5000/health

# Login
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin1@zatvia.com","password":"Todo####"}'

# List todos (use access token from login)
curl http://localhost:5000/todos \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Development Workflow

### Typical Development Session

```bash
# 1. Start fresh
make clean
make install

# 2. Initialize database with test data
make db-reinit

# 3. Start development server
make run-dev

# 4. In another terminal, test the API
make health
python scripts/manage.py login admin1@zatvia.com "Todo####"
python scripts/manage.py todos list
```

### Code Changes

The development server (`make run-dev`) automatically reloads when you change Python files.

### Running Tests

```bash
# Run all tests
make test

# Run with coverage report
make test-cov

# Run specific test
uv run pytest tests/test_todos.py -v
```

## Troubleshooting

### Port Already in Use

```bash
# Stop any running Flask servers
make stop

# Or manually
pkill -f "flask run"
pkill -f "python main.py"

# Check what's using port 5000
lsof -i :5000
```

### Database Connection Issues

1. Check PostgreSQL is running:
   ```bash
   psql -U todo_user -d todo_nestjs_dev -h localhost
   ```

2. Verify DATABASE_URL in `.env`:
   ```
   DATABASE_URL=postgresql://todo_user:todo_password_dev@localhost:5432/todo_nestjs_dev
   ```

3. Test database connectivity:
   ```bash
   make readiness
   ```

### Module Not Found Errors

```bash
# Reinstall dependencies
make clean
make install
```

### Virtual Environment Issues

```bash
# Remove and recreate venv
rm -rf .venv
uv venv
make install
```

## Production Deployment

### Using Gunicorn (Recommended)

```bash
# Install gunicorn if not already installed
uv pip install gunicorn

# Run with 4 worker processes
make run-prod

# Or manually with more control
uv run gunicorn -w 4 -b 0.0.0.0:5000 \
  --access-logfile - \
  --error-logfile - \
  --log-level info \
  "main:app"
```

### Environment Setup

1. Set `FLASK_ENV=production` in `.env`
2. Use strong JWT secrets (generate with `openssl rand -base64 32`)
3. Configure proper CORS origins
4. Set up database with connection pooling
5. Use a reverse proxy (nginx) in front of Gunicorn

## All Available Make Commands

Run `make help` to see all commands:

```bash
make help
```

Key commands:
- `make quickstart` - Quick setup (install + db-reinit)
- `make run-dev` - Start development server
- `make run` - Start production server
- `make run-prod` - Start with Gunicorn
- `make db-init` - Initialize database
- `make db-reinit` - Reset database with test data
- `make test` - Run tests
- `make clean` - Clean up generated files
- `make health` - Check API health
- `make stop` - Stop running server

## Comparison with NestJS

Similar commands across both backends:

| Task | NestJS | Flask |
|------|--------|-------|
| Install deps | `pnpm install` | `make install` or `uv sync` |
| Run dev server | `pnpm run start:dev` | `make run-dev` |
| Run prod server | `pnpm run start:prod` | `make run-prod` |
| Database reinit | `pnpm run db:reinit` | `make db-reinit` |
| Run tests | `pnpm test` | `make test` |
| API docs | http://localhost:3000/api | http://localhost:5000/docs |

Both use the same database and are fully compatible!
