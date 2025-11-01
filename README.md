# Todo App Monorepo

A production-ready full-stack Todo application with authentication, built as a monorepo supporting multiple backend and frontend implementations.

## 🏗️ Monorepo Structure

```
todo-app/
├── apps/
│   ├── api-nestjs/          # NestJS backend implementation
│   ├── frontend-nextjs/     # Next.js SPA frontend
│   └── [future backends]    # api-fastify, api-express, etc.
├── packages/
│   ├── database/            # Shared Drizzle ORM schemas & types
│   └── shared/              # Shared validation, constants, utilities
├── pnpm-workspace.yaml      # pnpm workspace configuration
└── package.json             # Root workspace scripts
```

## 🚀 Quick Start

### Prerequisites

- Node.js >= 18.0.0
- pnpm >= 8.0.0
- Docker & Docker Compose (for PostgreSQL)

### Installation

```bash
# Install all dependencies
pnpm install

# Start PostgreSQL and Adminer
pnpm docker:up

# Run database migrations
pnpm migration:run

# (Optional) Initialize database with test data
pnpm db:reinit
```

### Development

```bash
# Start NestJS API (development mode)
pnpm dev:api

# Start Next.js frontend (in another terminal)
pnpm dev:frontend

# Or run both concurrently (if you have concurrently installed)
pnpm dev
```

## 📦 Packages

### `@todo-app/database`

Shared database schemas and types using Drizzle ORM.

**Exports:**
- Database schemas: `users`, `todos`, `auditLogs`, etc.
- Clean types: `PublicUser`, `Todo`, `TodoWithOwner`
- Enums: `UserRole`, `TodoPriority`
- API types: `AuthResponse`, `PaginatedResponse`, etc.

**Usage:**
```typescript
import { PublicUser, Todo, UserRole } from '@todo-app/database';
```

### `@todo-app/shared`

Shared utilities, validation schemas, and constants.

**Exports:**
- Validation: `registerInputSchema`, `loginInputSchema`, etc.
- Constants: `ErrorCode`, `PASSWORD_RULES`, `TOKEN_EXPIRY`
- Utils: `formatError`, `isValidEmail`, etc.

**Usage:**
```typescript
import { registerInputSchema, ErrorCode } from '@todo-app/shared';
```

## 🔧 Available Scripts

### Root Level

```bash
pnpm build              # Build all packages and apps
pnpm test               # Run tests in all workspaces
pnpm lint               # Lint all workspaces
pnpm format             # Format all workspaces

# Docker
pnpm docker:up          # Start PostgreSQL + Adminer
pnpm docker:down        # Stop and remove containers

# Database
pnpm db:reinit          # Reset DB with test data
pnpm db:studio          # Open Drizzle Studio
pnpm migration:generate # Generate new migration
pnpm migration:run      # Run pending migrations

# Development
pnpm dev:api            # Start NestJS API
pnpm dev:frontend       # Start Next.js frontend
pnpm build:api          # Build NestJS API
pnpm build:frontend     # Build Next.js frontend
```

## 🗄️ Database

### Access Adminer

- URL: http://localhost:8080
- System: PostgreSQL
- Server: postgres
- Username: todo_user
- Password: todo_password_dev
- Database: todo_nestjs_dev

### Test Users (after `pnpm db:reinit`)

```
guest1@example.com     / Guest@123      (role: guest)
admin1@example.com     / Admin@123      (role: admin)
sysadmin1@example.com  / Sysadmin@123   (role: sysadmin)
```

## 🎯 API Endpoints

### NestJS API
- Base URL: http://localhost:3000
- GraphQL Playground: http://localhost:3000/graphql
- Health Check: http://localhost:3000/health
- Drizzle Studio: http://localhost:4983

### REST API Examples

```bash
# Register
curl -X POST http://localhost:3000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Pass@123","fullName":"User Name"}'

# Login
curl -X POST http://localhost:3000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"guest1@example.com","password":"Guest@123"}'

# Get todos (with Bearer token)
curl http://localhost:3000/todos \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🏛️ Architecture

### Type Safety Across Stack

All apps share the same types from `@todo-app/database`:

```typescript
// Backend (NestJS)
import { User, Todo } from '@todo-app/database';

// Frontend (Next.js)
import { PublicUser, TodoPriority } from '@todo-app/database';
```

### Adding New Backends

1. Create new app: `apps/api-fastify/`
2. Add dependencies in package.json:
   ```json
   {
     "dependencies": {
       "@todo-app/database": "workspace:*",
       "@todo-app/shared": "workspace:*"
     }
   }
   ```
3. Import shared types and schemas
4. Implement API using your framework

### Adding New Frontends

Same process as backends - create in `apps/frontend-<framework>/` and import from workspace packages.

## 📚 Tech Stack

### Backend (NestJS)
- **Framework:** NestJS
- **ORM:** Drizzle ORM
- **Database:** PostgreSQL
- **Auth:** JWT (access + refresh tokens)
- **Password Hashing:** Argon2id
- **Email:** SendGrid / SMTP
- **API:** REST + GraphQL

### Frontend (Next.js)
- **Framework:** Next.js 15 (App Router)
- **UI:** React 19
- **Types:** Shared from `@todo-app/database`

### Shared Packages
- **Validation:** Zod
- **Schema Management:** Drizzle Kit

## 🔐 Security Features

- ✅ Argon2id password hashing
- ✅ JWT access tokens (15min, in-memory)
- ✅ JWT refresh tokens (7 days, localStorage)
- ✅ Refresh token rotation
- ✅ Email verification required
- ✅ Rate limiting
- ✅ RBAC (guest, admin, sysadmin)
- ✅ Audit logging
- ✅ Session management

## 📝 License

UNLICENSED (Private)
