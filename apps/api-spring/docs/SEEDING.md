# Database Seeding

This document describes the database seeding functionality for the Spring Boot Todo App.

## Overview

The database seeding feature provides a convenient way to populate the database with demo users and todos for testing and development purposes. It mirrors the functionality of the FastAPI `seed_demo.py` script.

## Implementation

### Architecture

**DatabaseSeeder Service** (`src/main/java/com/todoapp/infrastructure/seeding/DatabaseSeeder.java`)
- Core seeding logic
- Transactional execution
- Idempotent (safe to run multiple times)
- Checks for existing users before creating

**SeedingConfig** (`src/main/java/com/todoapp/config/SeedingConfig.java`)
- CommandLineRunner bean activated by property
- Exits application after seeding completes
- Conditional on `spring.seed.enabled=true`

**Gradle Task** (`build.gradle.kts`)
- `seedDatabase` task in the `application` group
- Sets required system property automatically
- Displays database connection info

## Usage

### Quick Start

```bash
cd apps/api-spring

# Ensure database is running
docker-compose up -d

# Run migrations (if not already done)
./gradlew flywayMigrate

# Seed the database
./gradlew seedDatabase
```

### Output Example

```
🌱 Starting database seeding...
   Database: jdbc:postgresql://localhost:5434/todo_spring_dev

🌱 Seeding database with demo data...
  ✓ Created user: guest1@domain.com (guest)
  ✓ Created user: guest2@domain.com (guest)
  ✓ Created user: admin1@domain.com (admin)
  ✓ Created user: admin2@domain.com (admin)
  ✓ Created user: sysadmin1@domain.com (sysadmin)
  ✓ Created todo for guest1@domain.com: Buy groceries for the week
  ✓ Created todo for guest1@domain.com: Complete project documentation
  ✓ Created todo for guest1@domain.com: Call dentist for appointment
  ✓ Created todo for guest2@domain.com: Review pull requests
  ✓ Created todo for guest2@domain.com: Plan team meeting agenda

✅ Database seeded successfully!

Demo credentials (password: Todo####):
  Email: guest1@domain.com
  Email: admin1@domain.com
  Email: sysadmin1@domain.com
```

## Demo Data Created

### Users

| Email | Full Name | Role | Password | Email Verified | Todos |
|-------|-----------|------|----------|----------------|-------|
| guest1@domain.com | Guest User 1 | guest | Todo#### | ✅ | 3 |
| guest2@domain.com | Guest User 2 | guest | Todo#### | ✅ | 2 |
| admin1@domain.com | Admin User 1 | admin | Todo#### | ✅ | 0 |
| admin2@domain.com | Admin User 2 | admin | Todo#### | ✅ | 0 |
| sysadmin1@domain.com | Sysadmin User 1 | sysadmin | Todo#### | ✅ | 0 |

### Todos

**Guest1's Todos:**
1. "Buy groceries for the week" - High priority, due in 2 days
2. "Complete project documentation" - Medium priority, due in 7 days
3. "Call dentist for appointment" - Low priority, no due date

**Guest2's Todos:**
1. "Review pull requests" - High priority, due in 1 day
2. "Plan team meeting agenda" - Medium priority, due in 3 days

## Features

### Idempotent Execution

The seeder checks for existing users by email before creating them:

```java
UserRepository.User existingUser = userRepository.findByEmail(email).orElse(null);
if (existingUser != null) {
    log.info("  ⏭  User already exists: {}", email);
    createdUsers.add(existingUser);
    continue;
}
```

This makes it safe to run the seeder multiple times without creating duplicates.

### Transactional

The entire seeding operation runs in a single transaction:

```java
@Transactional
public void seed() {
    // All operations succeed or fail together
}
```

### Password Hashing

All demo users use the same password (`Todo####`) which is properly hashed using Argon2:

```java
String hashedPassword = passwordEncoder.encode(DEFAULT_PASSWORD);
```

### Email Verification

All demo users are created with verified email addresses for immediate testing:

```java
userRepository.markEmailVerified(userId);
```

## Testing the Demo Data

### Login as Guest

```bash
curl -X POST http://localhost:9000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "guest1@domain.com",
    "password": "Todo####"
  }'
```

### Login as Admin

```bash
curl -X POST http://localhost:9000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin1@domain.com",
    "password": "Todo####"
  }'
```

### Login as Sysadmin

```bash
curl -X POST http://localhost:9000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "sysadmin1@domain.com",
    "password": "Todo####"
  }'
```

### View Todos

```bash
# Get access token from login response
ACCESS_TOKEN="..."

# List todos (guests see own, admins see all)
curl http://localhost:9000/todos \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### Test Admin Endpoints

```bash
# Login as admin or sysadmin
ADMIN_TOKEN="..."

# List all users
curl http://localhost:9000/admin/users \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

## Customization

### Changing the Domain

Edit `DatabaseSeeder.java` and change the `DOMAIN` constant:

```java
private static final String DOMAIN = "yourdomain.com";
```

### Changing the Password

Edit `DatabaseSeeder.java` and change the `DEFAULT_PASSWORD` constant:

```java
private static final String DEFAULT_PASSWORD = "YourPassword123";
```

### Adding More Users

Add entries to the `demoUsers` list in `DatabaseSeeder.seed()`:

```java
List<DemoUser> demoUsers = List.of(
    new DemoUser("guest1@" + DOMAIN, "Guest User 1", Role.GUEST),
    new DemoUser("guest2@" + DOMAIN, "Guest User 2", Role.GUEST),
    // Add more users here
);
```

### Adding More Todos

Add entries to the `demoTodos` list in `DatabaseSeeder.seed()`:

```java
List<DemoTodo> demoTodos = List.of(
    new DemoTodo("Buy groceries", Priority.HIGH, now.plus(2, ChronoUnit.DAYS)),
    // Add more todos here
);
```

## Integration with CI/CD

### Docker Compose Integration

For containerized environments, you can add seeding as a one-time initialization:

```yaml
services:
  api-spring-seed:
    image: todo-app-spring:latest
    environment:
      - SPRING_SEED_ENABLED=true
      - SPRING_DATABASE_URL=jdbc:postgresql://postgres-spring:5432/todo_spring_dev
    depends_on:
      - postgres-spring
    restart: "no"  # Run once and exit
```

### GitHub Actions

```yaml
- name: Seed database
  run: |
    cd apps/api-spring
    ./gradlew seedDatabase
```

### Kubernetes Init Container

```yaml
initContainers:
  - name: seed-database
    image: todo-app-spring:latest
    env:
      - name: SPRING_SEED_ENABLED
        value: "true"
```

## Troubleshooting

### Database Connection Errors

Ensure PostgreSQL is running and migrations are applied:

```bash
docker-compose ps
./gradlew flywayMigrate
```

### Duplicate Key Errors

If you see duplicate key errors, the users likely already exist. The seeder will skip them automatically on subsequent runs.

### Password Hash Errors

Ensure Argon2PasswordEncoder bean is properly configured in `SecurityConfig.java`.

## Related Files

- **DatabaseSeeder.java** - Core seeding logic
- **SeedingConfig.java** - Spring Boot configuration
- **build.gradle.kts** - Gradle task definition
- **UserRepository.java** - User data access
- **TodoRepository.java** - Todo data access

## See Also

- [README.md](../README.md) - Main documentation
- [PHASE4_SUMMARY.md](../PHASE4_SUMMARY.md) - Core business logic implementation
- [PHASE5_SUMMARY.md](../PHASE5_SUMMARY.md) - Admin endpoints implementation
