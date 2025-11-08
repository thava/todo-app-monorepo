# Testing Strategy

## Overview

The Flask API uses a **two-tier testing strategy** to ensure code quality without compromising production compatibility:

1. **Unit Tests** - No database required, test business logic
2. **Integration Tests** - Require PostgreSQL, test full API endpoints

## Why Not SQLite for Tests?

**The production code uses PostgreSQL-specific features that are incompatible with SQLite:**

- ✅ **UUID** columns (PostgreSQL native type)
- ✅ **JSONB** columns (PostgreSQL-specific, not just JSON)
- ✅ **Enum** types (role, priority enums)
- ✅ **Timezone-aware** timestamps

**We preserve the exact schema** matching the NestJS backend in `./packages/database/src/schema/`, which means:
- No SQLite-specific workarounds
- Production code stays clean
- Database compatibility is guaranteed

## Test Structure

```
tests/
├── conftest.py              # Pytest fixtures (requires PostgreSQL)
├── test_todos_unit.py       # Unit tests (NO database)
├── test_todos.py            # Integration tests (PostgreSQL)
└── README.md               # Test documentation
```

## Unit Tests (No Database)

**File**: `tests/test_todos_unit.py`

**What they test**:
- ✅ Password validation logic
- ✅ Password hashing/verification
- ✅ Token generation and hashing
- ✅ Enum values (roles, priorities)
- ✅ Model serialization (to_dict methods)

**Run**:
```bash
pytest tests/test_todos_unit.py -v
```

**Coverage**:
- 17 tests
- All passing ✅
- No database required

**Example tests**:
```python
def test_password_validation_too_short():
    result = PasswordService.validate_password_strength('Short1')
    assert not result['is_valid']
    assert any('8 characters' in err for err in result['errors'])

def test_password_hash_and_verify():
    password_hash = PasswordService.hash_password('TestPassword123')
    assert PasswordService.verify_password(password_hash, 'TestPassword123')
```

## Integration Tests (PostgreSQL Required)

**File**: `tests/test_todos.py`

**What they test**:
- ✅ Full API endpoints (POST, GET, PATCH, DELETE)
- ✅ Authentication & authorization
- ✅ Role-based access control
- ✅ Database operations
- ✅ Request/response validation
- ✅ Error handling

**Setup**:
```bash
# 1. Create test database
createdb todo_test_db

# 2. Set environment variable
export TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/todo_test_db

# 3. Run tests
pytest tests/test_todos.py -v
```

**Coverage**:
- 40+ tests covering:
  - Create operations (6 tests)
  - Read operations (8 tests)
  - Update operations (8 tests)
  - Delete operations (5 tests)
  - Ownership & access control (2 tests)
  - Validation (4 tests)

**Example tests**:
```python
def test_create_todo_success(client, auth_headers):
    response = client.post('/todos',
        headers=auth_headers,
        json={'description': 'Test todo', 'priority': 'high'}
    )
    assert response.status_code == 201
    assert response.get_json()['description'] == 'Test todo'

def test_get_own_todos_only(client, auth_headers, admin_headers):
    # User creates todos
    client.post('/todos', headers=auth_headers, json={'description': 'User todo'})

    # Admin creates todos
    client.post('/todos', headers=admin_headers, json={'description': 'Admin todo'})

    # User should only see their own
    response = client.get('/todos', headers=auth_headers)
    assert len(response.get_json()) == 1
```

## Running Tests

### Quick Start (Unit Tests Only)

```bash
# Install dependencies
uv sync --all-extras

# Run unit tests (no setup needed)
pytest tests/test_todos_unit.py -v
```

### Full Test Suite (With PostgreSQL)

```bash
# 1. Create test database
createdb todo_test_db

# 2. Configure environment
export TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/todo_test_db

# 3. Run all tests
pytest -v

# 4. With coverage
pytest --cov=src --cov-report=html
```

### Continuous Integration

For CI/CD pipelines:

```yaml
# GitHub Actions example
jobs:
  test:
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: todo_test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Install dependencies
        run: uv sync --all-extras

      - name: Run unit tests
        run: pytest tests/test_todos_unit.py -v

      - name: Run integration tests
        env:
          TEST_DATABASE_URL: postgresql://postgres:postgres@localhost:5432/todo_test_db
        run: pytest tests/test_todos.py -v
```

## Test Fixtures

### Available Fixtures

| Fixture | Type | Description |
|---------|------|-------------|
| `app` | Flask app | Test application with PostgreSQL |
| `client` | Test client | HTTP client for API requests |
| `auth_headers` | Dict | Auth headers for guest user |
| `admin_headers` | Dict | Auth headers for admin user |
| `sysadmin_headers` | Dict | Auth headers for sysadmin user |

### Test Users

| Email | Password | Role | Verified |
|-------|----------|------|----------|
| test@example.com | Test1234 | guest | ✅ |
| admin@example.com | Admin1234 | admin | ✅ |
| sysadmin@example.com | Sysadmin1234 | sysadmin | ✅ |

## Best Practices

### DO ✅

- Write unit tests for business logic (no database)
- Write integration tests for API endpoints (with database)
- Use fixtures for authentication
- Test error cases and edge cases
- Keep production code PostgreSQL-compatible

### DON'T ❌

- Modify production code to support SQLite
- Skip testing because PostgreSQL isn't available (use unit tests)
- Hardcode test database credentials
- Leave test data in the database (fixtures cleanup automatically)

## Troubleshooting

### "PostgreSQL test database not configured"

**Solution**: Set the `TEST_DATABASE_URL` environment variable:
```bash
export TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/todo_test_db
```

### "Database does not exist"

**Solution**: Create the test database:
```bash
createdb todo_test_db
```

### Integration tests are slow

**Reason**: Each test creates and drops all tables for isolation.

**Solution**:
1. Run unit tests during development (fast)
2. Run integration tests before committing (slower but comprehensive)

### Want to run tests without PostgreSQL?

**Solution**: Run only unit tests:
```bash
pytest tests/test_todos_unit.py -v
```

## Test Coverage Summary

### Unit Tests: 17 tests ✅
- Password service: 7 tests
- Token service: 3 tests
- Enums: 4 tests
- Model serialization: 3 tests

### Integration Tests: 40+ tests (require PostgreSQL)
- Todo CRUD: 27 tests
- Access control: 13 tests
- Validation: 4 tests

### Total: 57+ tests

## Future Enhancements

Potential additions:
- `test_auth.py` - Authentication endpoint tests
- `test_users.py` - User profile tests
- `test_admin.py` - Admin operations tests
- `test_health.py` - Health check tests
- Performance tests
- Load tests with locust/k6

## Summary

**We maintain PostgreSQL compatibility in production code while providing:**
1. **Fast unit tests** for development (no database)
2. **Comprehensive integration tests** for confidence (PostgreSQL)
3. **Clean production code** that matches NestJS schema exactly

This approach ensures we can test effectively without compromising production quality! 🎯
