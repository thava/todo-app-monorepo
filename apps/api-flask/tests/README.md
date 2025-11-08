# Flask API Tests

## Test Types

### Unit Tests (No Database Required)
- **File**: `test_todos_unit.py`
- **Purpose**: Test business logic, validation, services
- **Database**: None required
- **Run**: `pytest tests/test_todos_unit.py`

### Integration Tests (PostgreSQL Required)
- **File**: `test_todos.py`
- **Purpose**: Test API endpoints, database operations
- **Database**: PostgreSQL test database required
- **Setup**: Set `TEST_DATABASE_URL` environment variable

## Running Tests

### Install Test Dependencies

```bash
# Install dev dependencies including pytest
uv sync --all-extras
```

### Run Unit Tests (No Database)

```bash
# These tests run without any database
pytest tests/test_todos_unit.py -v
```

### Run Integration Tests (PostgreSQL Required)

```bash
# Set test database URL
export TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/todo_test_db

# Run integration tests
pytest tests/test_todos.py -v
```

### Run All Tests

```bash
# With PostgreSQL configured
export TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/todo_test_db
pytest -v

# Without PostgreSQL (unit tests only)
pytest tests/test_todos_unit.py -v
```

### Run Specific Test Files

```bash
# Run only todo tests
pytest tests/test_todos.py

# Run specific test class
pytest tests/test_todos.py::TestTodoCreate

# Run specific test
pytest tests/test_todos.py::TestTodoCreate::test_create_todo_success
```

### Run with Verbose Output

```bash
pytest -v
```

### Run and Stop on First Failure

```bash
pytest -x
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Pytest fixtures and configuration
├── test_todos.py        # Todo CRUD tests
└── README.md           # This file
```

## Test Coverage

### Todo CRUD Tests (`test_todos.py`)

**Create Operations:**
- ✅ Create todo successfully
- ✅ Create with due date
- ✅ Create with minimal fields (defaults)
- ✅ Unauthorized access (401)
- ✅ Missing required fields (400)
- ✅ Invalid priority validation (400)

**Read Operations:**
- ✅ Get all todos (empty list)
- ✅ Get all todos (with data)
- ✅ Regular users see only own todos
- ✅ Admin users see all todos
- ✅ Get specific todo by ID
- ✅ Todo not found (404)
- ✅ Cannot access other users' todos (403)
- ✅ Unauthorized access (401)

**Update Operations:**
- ✅ Update description
- ✅ Update priority
- ✅ Update due date
- ✅ Update multiple fields
- ✅ Todo not found (404)
- ✅ Cannot update other users' todos (403)
- ✅ Sysadmin can update any todo
- ✅ Invalid priority validation (400)

**Delete Operations:**
- ✅ Delete todo successfully
- ✅ Todo not found (404)
- ✅ Cannot delete other users' todos (403)
- ✅ Sysadmin can delete any todo
- ✅ Unauthorized access (401)

**Ownership & Access Control:**
- ✅ Owner info included in response
- ✅ Multiple users have separate todo lists
- ✅ Role-based access control

**Validation:**
- ✅ Empty description validation
- ✅ Long description accepted
- ✅ Invalid date format
- ✅ Past due dates allowed

## Fixtures

### `app`
Creates a test Flask application with in-memory SQLite database.

### `client`
Provides a test client for making HTTP requests.

### `auth_headers`
Creates a regular user (guest role) and returns authentication headers.

### `admin_headers`
Creates an admin user and returns authentication headers.

### `sysadmin_headers`
Creates a sysadmin user and returns authentication headers.

## Test Users

| Fixture | Email | Password | Role | Email Verified |
|---------|-------|----------|------|----------------|
| `auth_headers` | test@example.com | Test1234 | guest | ✅ |
| `admin_headers` | admin@example.com | Admin1234 | admin | ✅ |
| `sysadmin_headers` | sysadmin@example.com | Sysadmin1234 | sysadmin | ✅ |

## Writing New Tests

### Basic Test Template

```python
def test_something(client, auth_headers):
    """Test description"""
    response = client.post('/todos',
        headers=auth_headers,
        json={'description': 'Test'}
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data['description'] == 'Test'
```

### Testing Different Roles

```python
def test_admin_access(client, admin_headers):
    """Test with admin user"""
    response = client.get('/todos', headers=admin_headers)
    assert response.status_code == 200

def test_sysadmin_access(client, sysadmin_headers):
    """Test with sysadmin user"""
    response = client.delete(f'/todos/{todo_id}', headers=sysadmin_headers)
    assert response.status_code == 204
```

### Testing Unauthorized Access

```python
def test_no_auth(client):
    """Test without authentication"""
    response = client.get('/todos')
    assert response.status_code == 401
```

## CI/CD Integration

Add to your CI/CD pipeline:

```yaml
# GitHub Actions example
- name: Run tests
  run: |
    uv sync --dev
    uv run pytest --cov=src --cov-report=xml
```

## Coverage Report

After running tests with coverage:

```bash
# Generate HTML coverage report
uv run pytest --cov=src --cov-report=html

# Open in browser
open htmlcov/index.html
```

## Troubleshooting

### Import Errors

Make sure you're running tests from the project root:
```bash
cd apps/api-flask
pytest
```

### Database Errors

Tests use in-memory SQLite, so database issues shouldn't occur. If they do, check `conftest.py`.

### Authentication Failures

If auth tests fail, check that:
- Password validation requirements are met
- Email verification is set correctly
- JWT secrets are configured

## Next Steps

Additional test files to add:
- `test_auth.py` - Authentication tests (register, login, refresh, etc.)
- `test_users.py` - User profile tests
- `test_admin.py` - Admin operations tests
- `test_health.py` - Health check tests
