# Audit Log Schema - Flask Implementation

## Overview

The audit logs table tracks all important actions in the system. The schema is defined in Drizzle (`packages/database/src/schema/audit-logs.schema.ts`) and used by both NestJS and Flask backends.

## Schema Fields

| Field | Type | Nullable | Purpose | Example Values |
|-------|------|----------|---------|----------------|
| `id` | UUID | No | Primary key | `550e8400-e29b-41d4-a716-446655440000` |
| `user_id` | UUID | Yes | User who performed the action (FK to users) | `123e4567-e89b-12d3-a456-426614174000` |
| `action` | VARCHAR(100) | No | Action performed | `LOGIN_SUCCESS`, `TODO_CREATED` |
| `entity_type` | VARCHAR(50) | Yes | Type of entity affected | `auth`, `todo`, `user` |
| `entity_id` | UUID | Yes | ID of the entity affected | Todo ID, User ID |
| `metadata` | JSONB | Yes | Additional context data | `{"email": "user@example.com", "role": "admin"}` |
| `ip_address` | VARCHAR(45) | Yes | Client IP address | `192.168.1.1`, `::1` |
| `user_agent` | TEXT | Yes | Client user agent | `Mozilla/5.0...` |
| `created_at` | TIMESTAMP | No | When the log was created | `2025-11-08 18:59:10` |

## Field Usage in NestJS

### entity_type
Categorizes what type of entity the action relates to:
- `'auth'` - Authentication/authorization events
- `'todo'` - Todo-related actions
- `'user'` - User management actions

### entity_id
The UUID of the specific entity being acted upon:
- For todo actions: the todo's UUID
- For user actions: the user's UUID
- For auth actions: typically `null`

### metadata
Additional structured data about the action:
```javascript
// Login example
{ email: 'user@example.com', success: true }

// Todo creation example
{ description: 'Buy groceries', priority: 'high' }

// Authorization failure example
{ requiredRole: 'admin', userRole: 'guest' }
```

## SQLAlchemy Implementation Issue

### The Problem

SQLAlchemy reserves the name `metadata` for internal use (the `MetaData` object that holds table definitions). You cannot use `metadata` as a column attribute name.

### The Solution

Use Python's column name mapping feature:

```python
# Define attribute as 'meta' but map to database column 'metadata'
meta = db.Column('metadata', JSONB, nullable=True)
```

This means:
- **In Python code**: Access as `audit_log.meta`
- **In database**: Column name is `metadata`
- **Fully compatible** with NestJS which uses `metadata`

## Flask Usage Examples

### Logging Authentication Events

```python
from src.services.audit_service import AuditService

# Login success
AuditService.log_auth(
    action='LOGIN_SUCCESS',
    user_id=str(user.id),
    metadata={'email': user.email, 'role': user.role.value},
    ip_address=request.remote_addr,
    user_agent=request.headers.get('User-Agent')
)

# Login failure
AuditService.log_auth(
    action='LOGIN_FAILURE',
    user_id=None,  # No user ID if user not found
    metadata={'email': email, 'reason': 'user_not_found'},
    ip_address=request.remote_addr,
    user_agent=request.headers.get('User-Agent')
)
```

### Logging Todo Actions

```python
# Todo created
AuditService.log_action(
    action='TODO_CREATED',
    user_id=str(current_user.id),
    entity_type='todo',
    entity_id=str(new_todo.id),
    metadata={'description': new_todo.description, 'priority': new_todo.priority.value},
    ip_address=request.remote_addr,
    user_agent=request.headers.get('User-Agent')
)

# Todo deleted
AuditService.log_action(
    action='TODO_DELETED',
    user_id=str(current_user.id),
    entity_type='todo',
    entity_id=str(todo.id),
    metadata={'description': todo.description},
    ip_address=request.remote_addr,
    user_agent=request.headers.get('User-Agent')
)
```

### Logging Admin Actions

```python
AuditService.log_action(
    action='ADMIN_USER_VIEWED',
    user_id=str(admin_user.id),
    entity_type='user',
    entity_id=str(target_user.id),
    metadata={'viewed_email': target_user.email},
    ip_address=request.remote_addr,
    user_agent=request.headers.get('User-Agent')
)
```

## Can These Fields Be Omitted?

**Yes!** All three fields (`entity_type`, `entity_id`, `metadata`) are **nullable** and **optional**.

### When to Include Them

**entity_type** - Include when you want to categorize the action:
```python
# Good - helps filtering audit logs by type
AuditService.log_action('TODO_CREATED', user_id=uid, entity_type='todo', ...)

# Also fine - minimal logging
AuditService.log_auth('LOGIN', user_id=uid, ...)
```

**entity_id** - Include when logging actions on specific entities:
```python
# Good - tracks which specific todo was modified
AuditService.log_action('TODO_UPDATED', entity_id=todo_id, ...)

# Also fine - auth events don't need entity_id
AuditService.log_auth('LOGIN_SUCCESS', user_id=uid, ...)
```

**metadata** - Include when you need additional context:
```python
# Good - rich context for auditing
AuditService.log_auth('LOGIN_FAILURE', metadata={'reason': 'invalid_password'}, ...)

# Also fine - minimal logging without context
AuditService.log_auth('LOGIN_SUCCESS', user_id=uid, ...)
```

### Minimal Usage Example

If you just want basic audit logging without detailed tracking:

```python
# Absolute minimum - just action required
AuditService.log_auth('LOGIN_SUCCESS', user_id=str(user.id))

# Still works fine! entity_type, entity_id, and metadata will be NULL
```

## Current Flask Implementation

The Flask implementation uses these fields strategically:

1. **Authentication events**:
   - Sets `entity_type='auth'`
   - Uses `metadata` for email, role, failure reasons
   - Omits `entity_id` (not needed for auth)

2. **Todo actions**: Could add (currently not implemented):
   - Set `entity_type='todo'`
   - Set `entity_id=todo.id`
   - Use `metadata` for description, priority changes

3. **User management**: Could add (currently not implemented):
   - Set `entity_type='user'`
   - Set `entity_id=target_user.id`
   - Use `metadata` for field changes

## Database Queries

Since these fields are nullable, you can query by them when needed:

```sql
-- Find all todo actions
SELECT * FROM audit_logs WHERE entity_type = 'todo';

-- Find all actions on a specific todo
SELECT * FROM audit_logs WHERE entity_id = '123e4567-e89b-12d3-a456-426614174000';

-- Find login failures
SELECT * FROM audit_logs
WHERE action = 'LOGIN_FAILURE'
AND metadata->>'reason' = 'invalid_password';

-- Find all auth events
SELECT * FROM audit_logs WHERE entity_type = 'auth';
```

## Summary

- **entity_type**, **entity_id**, and **metadata** are all **optional** (nullable)
- Use them for **richer audit trails** when needed
- **Minimal usage** is perfectly fine - just log the action
- In Python code, use `meta` attribute (maps to `metadata` column)
- The schema is **fully compatible** between NestJS and Flask
