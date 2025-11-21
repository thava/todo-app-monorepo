# Development Scripts

Utility scripts for development and debugging.

## Scripts Overview

### utils.py - Main CLI Utility

Comprehensive CLI tool for interacting with the API and database.

```bash
# User registration and authentication
python scripts/utils.py register test@example.com password123 "Test User"
python scripts/utils.py register admin@example.com password123 "Admin" --role=admin --autoverify
python scripts/utils.py login test@example.com password123
python scripts/utils.py logout
python scripts/utils.py me

# Todo management
python scripts/utils.py todos:list
python scripts/utils.py todos:create "Buy groceries" --priority=high --due="2025-12-31T23:59:59"
python scripts/utils.py todos:get <todo_id>
python scripts/utils.py todos:update <todo_id> --description="New description" --priority=low
python scripts/utils.py todos:delete <todo_id>

# Admin operations
python scripts/utils.py users:list
python scripts/utils.py users:get <user_id>

# Database operations
python scripts/utils.py db:status
python scripts/utils.py db:seed
python scripts/utils.py db:reinit  # ⚠️ Destroys all data!
```

### dev-utils.sh - Shell Functions

Sourceable shell script with utility functions for API testing.

```bash
# Source the script
source scripts/dev-utils.sh

# Use functions
register_user "test@example.com" "password123" "Test User"
login_user "test@example.com" "password123"
create_todo "Buy milk" "high" "2025-12-31T23:59:59"
list_todos
get_me
logout_user
```

### example-automation.sh - Example Workflow

Demonstrates a complete automated workflow:

```bash
./scripts/example-automation.sh
```

This script:
1. Registers a new user
2. Logs in
3. Creates several todos
4. Lists all todos
5. Updates a todo
6. Deletes a todo
7. Logs out

### shell.py - Interactive Python Shell

Open an interactive Python shell with app context pre-loaded:

```bash
python scripts/shell.py
```

Provides access to:
- `db`: Database session
- `settings`: App configuration
- Models: `User`, `Todo`, etc.
- Services: `auth_service`, `password_service`, `jwt_service`

Example usage in shell:
```python
>>> # Query users
>>> users = db.exec(select(User)).all()
>>> print(f"Total users: {len(users)}")

>>> # Query todos
>>> todos = db.exec(select(Todo).where(Todo.priority == PriorityEnum.HIGH)).all()

>>> # Create a user
>>> user = User(email="test@example.com", full_name="Test", ...)
>>> db.add(user)
>>> db.commit()
```

### seed_demo.py - Seed Demo Data

Populate database with demo users and todos:

```bash
python scripts/seed_demo.py
```

Creates:
- 2 guest users (guest1@domain.com, guest2@domain.com)
- 2 admin users (admin1@domain.com, admin2@domain.com)
- Sample todos for each guest user

All users have password: `Todo####`

## Token Management

Both `utils.py` and `dev-utils.sh` save authentication tokens to `.dev-tokens.json` for convenience during development.

**⚠️ Important**: This file contains sensitive tokens. It's in `.gitignore` but be careful not to commit it.

## Common Workflows

### Complete Test Workflow

```bash
# 1. Ensure database is running
make db-up

# 2. Run migrations
make migrate

# 3. Seed demo data
python scripts/seed_demo.py

# 4. Login as guest
python scripts/utils.py login guest1@domain.com Todo####

# 5. Create and manage todos
python scripts/utils.py todos:create "My new todo" --priority=high
python scripts/utils.py todos:list

# 6. Login as admin to see all todos
python scripts/utils.py login admin1@domain.com Todo####
python scripts/utils.py todos:list  # Shows all users' todos
python scripts/utils.py users:list
```

### Database Reset and Reseed

```bash
# Reset everything
python scripts/utils.py db:reinit

# Seed demo data
python scripts/seed_demo.py
```

### Interactive Debugging

```bash
# Open interactive shell
python scripts/shell.py

# Then in the shell:
>>> # Debug user issues
>>> user = db.exec(select(User).where(User.email == "test@example.com")).first()
>>> print(user.role, user.email_verified_at)

>>> # Check todos
>>> todos = db.exec(select(Todo)).all()
>>> for todo in todos:
...     print(f"{todo.description} - {todo.priority}")
```

## Tips

1. **Use Make targets**: Most common operations have Make targets:
   - `make dev` - Start dev server
   - `make test` - Run tests
   - `make db-up` - Start database
   - `make seed-demo` - Seed demo data

2. **Shell functions are reusable**: Source `dev-utils.sh` in your shell profile for persistent access

3. **Token persistence**: Tokens are saved between sessions, so you don't need to login repeatedly

4. **Database operations**: Use `db:status` frequently to check database state

5. **Interactive shell**: Great for debugging complex queries and testing business logic
