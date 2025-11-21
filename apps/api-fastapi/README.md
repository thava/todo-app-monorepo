# FastAPI Todo App Backend

Production-grade FastAPI backend implementation for the Todo App monorepo, following the NestJS API specification.

## Tech Stack

- **FastAPI** - Modern async web framework
- **SQLModel** - Type-safe ORM (SQLAlchemy + Pydantic)
- **Alembic** - Database migrations
- **PostgreSQL** - Database
- **Argon2** - Password hashing (via argon2-cffi)
- **PyJWT** - JWT token management
- **uv** - Fast Python package manager
- **Pyright** - Static type checking
- **Ruff** - Linting and code formatting
- **Pytest** - Testing framework
- **Docker** - Containerization

## Features

### Authentication & Authorization
- User registration with email verification
- Login with JWT access/refresh tokens
- Token refresh and logout
- Password reset flow
- Role-based access control (guest, admin, sysadmin)
- Email verification

### User Management
- Get/update current user profile
- Admin user management (CRUD operations)

### Todo Management
- Create, read, update, delete todos
- Role-based access (users see only their todos, admins see all)
- Priority levels (low, medium, high)
- Due dates

### Health & Monitoring
- `/health` - Liveness probe
- `/readiness` - Readiness probe with DB check

## Project Structure

```
apps/api-fastapi/
├── app/
│   ├── api/
│   │   ├── deps/          # Authentication dependencies
│   │   ├── routes/        # API endpoints
│   │   └── main.py        # Router configuration
│   ├── core/
│   │   ├── config.py      # Settings management
│   │   └── db.py          # Database connection
│   ├── models/            # SQLModel database models
│   ├── schemas/           # Pydantic DTOs
│   ├── services/          # Business logic services
│   ├── initial_data.py    # DB initialization
│   └── main.py            # FastAPI application
├── alembic/               # Database migrations
├── tests/                 # Test suite
├── Dockerfile             # Multi-stage production image
├── docker-compose.yml     # Local development setup
└── pyproject.toml         # Dependencies and tooling config
```

## Development Setup

### Prerequisites
- Python 3.10+
- PostgreSQL
- uv (Python package manager)

### Installation

1. Install dependencies:
```bash
uv sync
```

2. Set up environment variables:
```bash
cp ../../.env .env
# Edit .env with your configuration
```

3. Run database migrations:
```bash
uv run alembic upgrade head
```

4. Initialize database (creates sysadmin user in dev):
```bash
uv run python -m app.initial_data
```

5. Start development server:
```bash
uv run uvicorn app.main:app --reload --port 8000
```

The API will be available at http://localhost:8000

### API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/api/v1/openapi.json

## Docker

### Build and run with Docker Compose:

```bash
docker-compose up --build
```

### Build production image:

```bash
docker build -t todo-fastapi:latest .
```

## Testing

Run tests:
```bash
uv run pytest
```

With coverage:
```bash
uv run pytest --cov=app --cov-report=html
```

## Code Quality

### Linting

```bash
uv run ruff check app
```

Auto-fix issues:
```bash
uv run ruff check app --fix
```

### Type Checking

```bash
uv run pyright app
```

## Configuration

Key environment variables:

- `NODE_ENV` - Environment (development/production)
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_ACCESS_SECRET` - JWT access token secret
- `JWT_REFRESH_SECRET` - JWT refresh token secret
- `SENDGRID_API_KEY` or SMTP settings - Email configuration
- `CORS_ALLOWED_ORIGINS` - CORS allowed origins

See `.env` file for complete configuration options.

## Database Migrations

Create new migration:
```bash
uv run alembic revision --autogenerate -m "Description"
```

Apply migrations:
```bash
uv run alembic upgrade head
```

Rollback:
```bash
uv run alembic downgrade -1
```

## Default Credentials (Development)

When `NODE_ENV=development`, a sysadmin user is auto-created:

- Email: `sysadmin1@domain.com`
- Password: `Todo####`

## API Endpoints

### Public
- `GET /` - Root endpoint
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login
- `POST /auth/refresh` - Refresh access token
- `GET /auth/verify-email` - Verify email
- `POST /auth/request-password-reset` - Request password reset
- `POST /auth/reset-password` - Reset password

### Authenticated
- `GET /me` - Get current user profile
- `PATCH /me` - Update current user profile
- `POST /auth/logout` - Logout
- `POST /auth/resend-verification` - Resend verification email
- `GET /todos` - List todos
- `POST /todos` - Create todo
- `GET /todos/{id}` - Get todo
- `PATCH /todos/{id}` - Update todo
- `DELETE /todos/{id}` - Delete todo

### Admin Only
- `GET /admin/users` - List all users
- `GET /admin/users/{id}` - Get user by ID

### Sysadmin Only
- `PATCH /admin/users/{id}` - Update user
- `DELETE /admin/users/{id}` - Delete user

### Health
- `GET /health` - Health check
- `GET /readiness` - Readiness check

## Security

- Passwords hashed with Argon2 (industry-standard, more secure than bcrypt)
- JWT tokens with separate access/refresh tokens
- Refresh token rotation on use
- Role-based authorization
- Email verification for new accounts
- Password reset with secure tokens
- Token revocation on logout/password change

## Production Considerations

- ✅ Production-grade password hashing (Argon2)
- ✅ JWT token management with refresh token rotation
- ✅ Database migrations with Alembic
- ✅ Health check endpoints for orchestration
- ✅ Docker multi-stage builds
- ✅ Type checking with Pyright
- ✅ Linting with Ruff
- ✅ CORS configuration
- ✅ Environment-based configuration
- ✅ Proper error handling
- ⚠️ Email service (stub - needs SendGrid/SMTP implementation)
- ⚠️ Rate limiting (not implemented)

