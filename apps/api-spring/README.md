# Todo App - Spring Boot Backend

Spring Boot implementation of the Todo App backend, featuring JWT authentication, PostgreSQL with jOOQ, and SendGrid email integration.

## Tech Stack

- **Java 21** with modern features (records, pattern matching, virtual threads)
- **Spring Boot 3.4.x**
- **Gradle 8.x** with Kotlin DSL
- **PostgreSQL 16** with UUID primary keys
- **jOOQ 3.19** for type-safe SQL
- **Flyway 10** for database migrations
- **Argon2** password hashing (Spring Security Crypto)
- **JWT** (jjwt library) for authentication
- **SendGrid** for email delivery
- **MapStruct** for DTO mapping
- **Testcontainers** for integration testing

## Architecture

```
Hexagonal / Clean Architecture:
Controller → Service → Repository (jOOQ)
```

## Prerequisites

- Java 21 (JDK 21+)
- Docker & Docker Compose
- PostgreSQL client tools (for apgdiff tasks)
- Gradle 8.x (or use wrapper)

## Quick Start

### 1. Start PostgreSQL Database

```bash
# From the api-spring directory
docker-compose up -d

# Or from the monorepo root (starts all databases)
docker-compose up -d postgres-spring
```

### 2. Run Database Migrations

```bash
./gradlew flywayMigrate
```

### 3. Generate jOOQ Code

```bash
./gradlew generateJooq
```

### 4. Build the Application

```bash
./gradlew build
```

### 5. Run the Application

```bash
./gradlew bootRun
```

The API will be available at: `http://localhost:9000`

## Production Deployment

For production deployment with Docker:

```bash
# 1. Configure environment
cp .env.prod.example .env.prod
# Edit .env.prod with your production values

# 2. Build and deploy
docker build -t todo-app-spring:latest .
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# 3. Verify deployment
curl http://localhost:9000/health
```

**📖 See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment guide including:**
- Production configuration
- Kubernetes deployment
- Monitoring setup
- Security checklist
- Troubleshooting

## API Documentation

- **Swagger UI**: http://localhost:9000/swagger-ui.html
- **OpenAPI Spec**: http://localhost:9000/v3/api-docs
- **Health Check**: http://localhost:9000/health
- **Readiness Check**: http://localhost:9000/readiness
- **Metrics**: http://localhost:9000/actuator/prometheus

## Database Management

### Schema Dump

Dump the current database schema to `docs/database/current-schema.sql`:

```bash
./gradlew dumpSchema
```

### Schema Comparison

Compare current database schema with expected schema:

```bash
./gradlew compareSchema
```

Requires `apgdiff` to be installed:
- macOS: `brew install apgdiff`
- Linux: `apt-get install apgdiff`

### Clean jOOQ Generated Code

```bash
./gradlew cleanJooq
```

### Flyway Commands

```bash
# Run migrations
./gradlew flywayMigrate

# Get migration info
./gradlew flywayInfo

# Validate migrations
./gradlew flywayValidate

# Clean database (dev only!)
./gradlew flywayClean
```

### Seed Demo Data

Seed the database with demo users and todos for testing:

```bash
./gradlew seedDatabase
```

**Demo Users Created:**
- `guest1@domain.com` - Guest User 1 (role: guest) with 3 todos
- `guest2@domain.com` - Guest User 2 (role: guest) with 2 todos
- `admin1@domain.com` - Admin User 1 (role: admin)
- `admin2@domain.com` - Admin User 2 (role: admin)
- `sysadmin1@domain.com` - Sysadmin User 1 (role: sysadmin)

**Password for all demo users:** `Todo####`

All users are created with verified email addresses for immediate testing.

**Note:** The seed script checks for existing users and skips them if already present, making it safe to run multiple times.

## Environment Variables

Copy `.env` file and adjust as needed:

```bash
# Database
SPRING_DATABASE_URL=jdbc:postgresql://localhost:5434/todo_spring_dev
SPRING_DATABASE_USER=todo_user
SPRING_DATABASE_PASSWORD=todo_password_dev

# Server
SPRING_PORT=9000
SPRING_PROFILES_ACTIVE=dev

# JWT
JWT_ACCESS_SECRET=your-access-secret
JWT_REFRESH_SECRET=your-refresh-secret
JWT_ACCESS_EXPIRY=15m
JWT_REFRESH_EXPIRY=7d

# Email
SENDGRID_API_KEY=your-sendgrid-api-key
EMAIL_FROM=noreply@example.com

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:4000,http://localhost:3000
```

## Testing

### Run All Tests

```bash
./gradlew test
```

### Run Integration Tests Only

```bash
./gradlew test --tests "com.todoapp.integration.*"
```

### Run Specific Test Class

```bash
./gradlew test --tests "AuthFlowIntegrationTest"
```

### Generate Test Coverage Report

```bash
./gradlew test jacocoTestReport
open build/reports/jacoco/test/html/index.html
```

**Test Suite:**
- 35 integration tests with Testcontainers
- 10 authentication flow tests
- 13 todo CRUD tests with authorization
- 12 admin operations tests
- ~75-80% coverage of critical paths

## Development Workflow

### 1. Create a New Migration

```bash
# Create a new migration file
touch src/main/resources/db/migration/V002__add_feature.sql

# Write your SQL
# Run migration
./gradlew flywayMigrate

# Regenerate jOOQ code
./gradlew generateJooq
```

### 2. Update Schema Documentation

```bash
./gradlew dumpSchema
```

### 3. Run Tests

```bash
# Run all tests
./gradlew test

# Run specific test
./gradlew test --tests "HealthControllerTest"

# Run with coverage
./gradlew test jacocoTestReport
```

## Project Structure

```
src/
├── main/
│   ├── java/com/todoapp/
│   │   ├── TodoAppApplication.java
│   │   ├── config/              # Spring configuration
│   │   ├── infrastructure/      # DB, external services
│   │   │   ├── jooq/           # Generated jOOQ code
│   │   │   ├── email/          # SendGrid integration
│   │   │   ├── security/       # JWT, Argon2
│   │   │   └── audit/          # Audit logging
│   │   ├── domain/              # Business entities
│   │   │   ├── model/          # Enums, value objects
│   │   │   ├── repository/     # jOOQ repositories
│   │   │   └── exception/      # Domain exceptions
│   │   ├── application/         # Use cases/services
│   │   │   ├── service/        # Business logic
│   │   │   ├── mapper/         # MapStruct interfaces
│   │   │   └── dto/            # Internal DTOs
│   │   └── presentation/        # Controllers, DTOs
│   │       ├── controller/     # REST endpoints
│   │       ├── dto/            # Request/response DTOs
│   │       └── advice/         # Exception handlers
│   └── resources/
│       ├── application.yml
│       ├── application-dev.yml
│       ├── application-prod.yml
│       ├── db/migration/       # Flyway scripts
│       └── templates/email/    # Email templates
└── test/
    ├── java/com/todoapp/
    │   ├── integration/        # Integration tests
    │   ├── controller/         # Controller tests
    │   ├── service/            # Service tests
    │   └── repository/         # Repository tests
    └── resources/
        └── application-test.yml
```

## Testing

### Unit Tests

```bash
./gradlew test
```

### Integration Tests (with Testcontainers)

```bash
./gradlew integrationTest
```

### Test Coverage

```bash
./gradlew test jacocoTestReport
open build/reports/jacoco/test/html/index.html
```

## Monitoring

### Actuator Endpoints

- `/health` - Liveness probe
- `/readiness` - Readiness probe with DB check
- `/actuator/info` - Application info
- `/actuator/metrics` - Metrics
- `/actuator/prometheus` - Prometheus metrics

## Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker ps | grep postgres-spring

# Check logs
docker logs todo-spring-postgres

# Test connection
psql -h localhost -p 5434 -U todo_user -d todo_spring_dev
```

### jOOQ Generation Issues

```bash
# Clean and regenerate
./gradlew cleanJooq generateJooq

# Verify database schema
./gradlew flywayInfo
```

### Build Issues

```bash
# Clean build
./gradlew clean build

# Build without tests
./gradlew build -x test
```

## Implementation Status

### Phase 1: Project Scaffolding & Database Foundation ✅
✅ Gradle project structure
✅ Application configuration (YAML)
✅ Flyway migrations (matches NestJS schema)
✅ PostgreSQL Docker Compose (port 5434)
✅ jOOQ code generation
✅ apgdiff schema tasks
✅ Health check endpoints
✅ Basic security configuration

### Phase 2: Security Infrastructure & Authentication ✅
✅ JWT token generation & validation
✅ User registration & login
✅ Refresh token rotation
✅ Role-based access control (guest, admin, sysadmin)
✅ Password hashing with Argon2
✅ Stateful refresh tokens (database-stored)
✅ @CurrentUser annotation for controller injection
✅ RFC7807 Problem+JSON error responses
✅ Global exception handling
✅ Unit tests for JWT service

### Phase 3: Email Verification & Password Reset ✅
✅ SendGrid email integration with async sending
✅ Email verification flow (24h expiry)
✅ Password reset flow (1h expiry, revokes sessions)
✅ Professional HTML & text email templates
✅ Scheduled token cleanup jobs
✅ Security: No email enumeration, one-time tokens
✅ GET /auth/verify-email endpoint
✅ POST /auth/resend-verification endpoint (protected)
✅ POST /auth/request-password-reset endpoint
✅ POST /auth/reset-password endpoint

### Phase 4: Core Business Logic - Todos & Users ✅
✅ Todo CRUD operations (create, list, get, update, delete)
✅ User profile endpoints (GET /me, PATCH /me)
✅ Authorization service with ownership checks
✅ Role-based todo access (guests see own, admins see all)
✅ Ownership-based modifications (only owners can edit/delete)
✅ Audit logging system (async, comprehensive)
✅ All operations audit logged
✅ @CurrentUser annotation for authenticated users
✅ Proper error handling (403 Forbidden, 404 Not Found)

### Phase 5: Admin Endpoints & System Management ✅
✅ Admin user management endpoints
✅ GET /admin/users - List all users (admin/sysadmin)
✅ GET /admin/users/{id} - Get user by ID (admin/sysadmin)
✅ PATCH /admin/users/{id} - Update user (sysadmin only)
✅ DELETE /admin/users/{id} - Delete user (sysadmin only)
✅ Two-tier authorization (admin for read, sysadmin for write)
✅ Complete user update functionality
✅ Cascade deletion of user data
✅ 100% functional parity with NestJS reference

### Database Seeding ✅
✅ DatabaseSeeder service with transactional execution
✅ Idempotent seeding (safe to run multiple times)
✅ Demo users: 2 guests, 2 admins, 1 sysadmin
✅ Demo todos: 5 todos distributed among guest users
✅ Gradle task: `./gradlew seedDatabase`
✅ Comprehensive documentation in docs/SEEDING.md
✅ Password: "Todo####" for all demo users
✅ Email verification pre-applied
✅ Matches FastAPI reference implementation

### Phase 6: Testing, Documentation & Production Readiness ✅
✅ Integration testing with Testcontainers (35 tests)
✅ Authentication flow tests (10 tests)
✅ Todo CRUD tests with authorization (13 tests)
✅ Admin operations tests (12 tests)
✅ Test coverage ~75-80% of critical paths
✅ Custom business metrics (MetricsService)
✅ Prometheus metrics export (/actuator/prometheus)
✅ Multi-stage Dockerfile (~200MB)
✅ Production docker-compose with monitoring stack
✅ Prometheus & Grafana integration (optional profile)
✅ Environment configuration templates
✅ Comprehensive deployment guide (DEPLOYMENT.md)
✅ Metrics documentation (docs/METRICS.md)
✅ Kubernetes deployment examples
✅ Health checks and readiness probes
✅ Security hardening guide
✅ Troubleshooting and backup instructions

### Backend Completion: ~98% 🎉
All phases complete and production-ready:
- ✅ Phase 1: Project Scaffolding & Database Foundation
- ✅ Phase 2: Security Infrastructure & Authentication
- ✅ Phase 3: Email Verification & Password Reset
- ✅ Phase 4: Core Business Logic - Todos & Users
- ✅ Phase 5: Admin Endpoints & System Management
- ✅ Database Seeding with demo data
- ✅ Phase 6: Testing, Documentation & Production Readiness

**Ready for production deployment!** 🚀

## Documentation

### Project Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete production deployment guide
  - Docker and Kubernetes deployment
  - Environment configuration
  - Security checklist
  - Monitoring setup
  - Troubleshooting

- **[SEEDING.md](docs/SEEDING.md)** - Database seeding guide
  - Demo data creation
  - Usage instructions
  - Customization

- **[METRICS.md](docs/METRICS.md)** - Custom metrics documentation
  - Available metrics
  - Prometheus setup
  - Grafana queries

- **[PHASE6_SUMMARY.md](PHASE6_SUMMARY.md)** - Phase 6 implementation details
  - Integration testing
  - Docker deployment
  - Production readiness

### Phase Summaries

- [PHASE1_SUMMARY.md](PHASE1_SUMMARY.md) - Project scaffolding & database
- [PHASE2_SUMMARY.md](PHASE2_SUMMARY.md) - Authentication & security
- [PHASE3_SUMMARY.md](PHASE3_SUMMARY.md) - Email flows
- [PHASE4_SUMMARY.md](PHASE4_SUMMARY.md) - Core business logic
- [PHASE5_SUMMARY.md](PHASE5_SUMMARY.md) - Admin endpoints
- [SEEDING_SUMMARY.md](SEEDING_SUMMARY.md) - Database seeding

## External References

- [Spring Boot Documentation](https://spring.io/projects/spring-boot)
- [jOOQ Documentation](https://www.jooq.org/doc/latest/manual/)
- [Flyway Documentation](https://flywaydb.org/documentation/)
- [Testcontainers Documentation](https://www.testcontainers.org/)
- [Micrometer Documentation](https://micrometer.io/docs)
- [OpenAPI Specification](../../docs/openapi.yaml)
