#!/usr/bin/env python3

"""
CLI Utility for Todo Flask API

Usage:
    python scripts/manage.py register test@example.com password123 "Test User"
    python scripts/manage.py login test@example.com password123
    python scripts/manage.py todos:create "Buy groceries" --priority=high --due="2025-12-31"
    python scripts/manage.py todos:list
    python scripts/manage.py todos:delete <todo_id>
    python scripts/manage.py db:reinit
"""

import os
import sys
import json
import click
from argon2 import PasswordHasher, Type
import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.app import create_app, db
from src.models.user import User, RoleEnum
from src.models.todo import Todo, PriorityEnum
from src.models.refresh_token_session import RefreshTokenSession
from src.models.email_verification_token import EmailVerificationToken
from src.models.password_reset_token import PasswordResetToken
from src.models.audit_log import AuditLog

# Load environment variables
env_path = Path(__file__).parent.parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    click.echo(f"✓ Loaded environment variables from {env_path}")
else:
    click.echo(f"⚠ No .env file found at {env_path}, using existing environment variables")

# Configuration
API_URL = os.getenv('FLASK_API_URL', 'http://localhost:5000')
TOKEN_FILE = Path.cwd() / '.dev-tokens.json'

# Colors for terminal output
class Colors:
    RESET = '\033[0m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'

# Helper functions
def print_success(message: str) -> None:
    click.echo(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_error(message: str) -> None:
    click.echo(f"{Colors.RED}✗ {message}{Colors.RESET}", err=True)

def print_info(message: str) -> None:
    click.echo(f"{Colors.BLUE}ℹ {message}{Colors.RESET}")

def print_warning(message: str) -> None:
    click.echo(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")

def print_json(data: Any) -> None:
    click.echo(json.dumps(data, indent=2))

# Token management
def save_tokens(access_token: str, refresh_token: str) -> None:
    token_data = {
        'accessToken': access_token,
        'refreshToken': refresh_token,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    TOKEN_FILE.write_text(json.dumps(token_data, indent=2))
    print_success(f"Tokens saved to {TOKEN_FILE}")

def load_tokens() -> Optional[Dict[str, str]]:
    if not TOKEN_FILE.exists():
        print_error(f"Token file not found: {TOKEN_FILE}")
        return None

    try:
        data = TOKEN_FILE.read_text()
        tokens = json.loads(data)
        print_success('Tokens loaded')
        return tokens
    except Exception as e:
        print_error(f"Failed to load tokens: {e}")
        return None

def clear_tokens() -> None:
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()
        print_success('Token file deleted')
    else:
        print_info('No token file to delete')

# HTTP helper
def api_request(
    endpoint: str,
    method: str = 'GET',
    body: Optional[Dict[str, Any]] = None,
    use_auth: bool = False
) -> tuple[int, Optional[Dict[str, Any]]]:
    headers = {'Content-Type': 'application/json'}

    if use_auth:
        tokens = load_tokens()
        if not tokens:
            raise Exception('No authentication tokens found. Please login first.')
        headers['Authorization'] = f"Bearer {tokens['accessToken']}"

    try:
        response = requests.request(
            method,
            f"{API_URL}{endpoint}",
            headers=headers,
            json=body,
            timeout=30
        )

        data = None
        if response.headers.get('content-type', '').startswith('application/json'):
            try:
                data = response.json()
            except json.JSONDecodeError:
                pass

        return response.status_code, data
    except Exception as e:
        print_error(f"API request failed: {e}")
        raise

# CLI group
@click.group()
def cli():
    """Todo Flask API - CLI Utility"""
    pass

# Database commands
@cli.group(name='db')
def db_group():
    """Database management commands"""
    pass

@db_group.command(name='init')
def db_init():
    """Initialize database tables"""
    app = create_app()
    with app.app_context():
        db.create_all()
        print_success('Database tables created successfully!')

@db_group.command(name='drop')
def db_drop():
    """Drop all database tables"""
    app = create_app()
    with app.app_context():
        db.drop_all()
        print_success('Database tables dropped successfully!')

@db_group.command(name='reinit')
def db_reinit():
    """Reinitialize database with test data"""
    print_info('Starting database reinitialization')

    app = create_app()
    with app.app_context():
        try:
            # Delete all data from tables (in reverse dependency order)
            print_info('Deleting all data from tables...')
            Todo.query.delete()
            EmailVerificationToken.query.delete()
            PasswordResetToken.query.delete()
            RefreshTokenSession.query.delete()
            AuditLog.query.delete()
            User.query.delete()
            db.session.commit()
            print_success('All tables cleared')

            # Get demo configuration from environment
            domain = os.getenv('DEMO_DOMAIN', 'mydomain.com')
            password = os.getenv('DEMO_PASSWORD', 'mypassword')
            user_list_str = os.getenv('DEMO_USERS', 'guest1,admin1,sysadmin1')
            user_list = user_list_str.split(',') if user_list_str else []

            test_users = []
            for username in user_list:
                email = f"{username}@{domain}"
                capitalized = username[0].upper() + username[1:]
                full_name = f"{capitalized} User"

                # Infer role from username prefix
                if username.startswith('guest'):
                    role = RoleEnum.guest
                elif username.startswith('admin'):
                    role = RoleEnum.admin
                elif username.startswith('sysadmin'):
                    role = RoleEnum.sysadmin
                else:
                    role = RoleEnum.guest

                test_users.append({
                    'email': email,
                    'password': password,
                    'fullName': full_name,
                    'role': role,
                    'username': username
                })

            print_info('Creating test users...')
            created_users = []

            # Argon2id hasher with same parameters as NestJS
            ph = PasswordHasher(
                time_cost=2,
                memory_cost=19456,
                parallelism=1,
                hash_len=32,
                salt_len=16,
                type=Type.ID  # Argon2id
            )

            for user_data in test_users:
                # Hash password using Argon2id
                password_hash = ph.hash(user_data['password'])

                # Create user with email already verified
                user = User(
                    email=user_data['email'],
                    full_name=user_data['fullName'],
                    password_hash_primary=password_hash,
                    role=user_data['role'],
                    email_verified_at=datetime.now(timezone.utc)
                )
                db.session.add(user)
                db.session.flush()  # Get the ID

                created_users.append({
                    'id': user.id,
                    'email': user.email,
                    'username': user_data['username']
                })
                print_success(f"Created user: {user_data['email']} ({user_data['role'].value}): {user_data['fullName']}")

            db.session.commit()

            # Create 3 todos for each user
            print_info('Creating todos for each user...')
            todo_templates = [
                {'action': 'to visit dentist', 'priority': PriorityEnum.high},
                {'action': 'to buy groceries', 'priority': PriorityEnum.medium},
                {'action': 'to finish project', 'priority': PriorityEnum.low},
            ]

            for user in created_users:
                for template in todo_templates:
                    todo = Todo(
                        owner_id=user['id'],
                        description=f"{user['username']} {template['action']}",
                        priority=template['priority']
                    )
                    db.session.add(todo)
                print_success(f"Created 3 todos for {user['email']}")

            db.session.commit()

            print_success('Database reinitialization completed successfully')
            print_info('\nTest accounts created:')
            for user_data in test_users:
                print_info(f"{user_data['email']} [Password: {user_data['password']}]")
            print_info('\n3 todos created per user')

        except Exception as e:
            db.session.rollback()
            print_error(f"Database reinitialization failed: {e}")
            raise

# Authentication commands
@cli.command()
@click.argument('email')
@click.argument('password')
@click.argument('full_name')
def register(email: str, password: str, full_name: str):
    """Register a new user"""
    print_info(f"Registering user: {email}")

    status, data = api_request('/auth/register', 'POST', {
        'email': email,
        'password': password,
        'fullName': full_name
    })

    if status == 201 and data:
        print_success('User registered successfully')
        print_json(data.get('user', {}))
        save_tokens(data['accessToken'], data['refreshToken'])
    else:
        print_error(f"Registration failed (HTTP {status})")
        if data:
            print_json(data)
        sys.exit(1)

@cli.command()
@click.argument('email')
@click.argument('password')
def login(email: str, password: str):
    """Login and save tokens"""
    print_info(f"Logging in: {email}")

    status, data = api_request('/auth/login', 'POST', {
        'email': email,
        'password': password
    })

    if status == 200 and data:
        print_success('Login successful')
        print_json(data.get('user', {}))
        save_tokens(data['accessToken'], data['refreshToken'])
    else:
        print_error(f"Login failed (HTTP {status})")
        if data:
            print_json(data)
        sys.exit(1)

@cli.command()
def refresh():
    """Refresh access token"""
    tokens = load_tokens()
    if not tokens:
        sys.exit(1)

    print_info('Refreshing access token')

    status, data = api_request('/auth/refresh', 'POST', {
        'refreshToken': tokens['refreshToken']
    })

    if status == 200 and data:
        print_success('Token refreshed successfully')
        save_tokens(data['accessToken'], data['refreshToken'])
    else:
        print_error(f"Token refresh failed (HTTP {status})")
        if data:
            print_json(data)
        sys.exit(1)

@cli.command()
def logout():
    """Logout and clear tokens"""
    tokens = load_tokens()
    if not tokens:
        sys.exit(1)

    print_info('Logging out')

    status, data = api_request('/auth/logout', 'POST', {
        'refreshToken': tokens['refreshToken']
    })

    if status == 204:
        print_success('Logout successful')
        clear_tokens()
    else:
        print_error(f"Logout failed (HTTP {status})")
        sys.exit(1)

@cli.command()
def profile():
    """Get current user profile"""
    print_info('Fetching user profile')

    status, data = api_request('/me', use_auth=True)

    if status == 200 and data:
        print_success('Profile retrieved')
        print_json(data)
    else:
        print_error(f"Failed to get profile (HTTP {status})")
        if data:
            print_json(data)
        sys.exit(1)

# Todo commands
@cli.group(name='todos')
def todos_group():
    """Todo operations"""
    pass

@todos_group.command(name='create')
@click.argument('description')
@click.option('--priority', type=click.Choice(['low', 'medium', 'high']), default='medium')
@click.option('--due', help='Due date in ISO format (e.g., 2025-12-31)')
def todos_create(description: str, priority: str, due: Optional[str]):
    """Create a new todo"""
    print_info(f"Creating todo: {description}")

    body = {'description': description, 'priority': priority}
    if due:
        body['dueDate'] = due

    status, data = api_request('/todos', 'POST', body, use_auth=True)

    if status == 201 and data:
        print_success('Todo created')
        print_json(data)
    else:
        print_error(f"Failed to create todo (HTTP {status})")
        if data:
            print_json(data)
        sys.exit(1)

@todos_group.command(name='list')
def todos_list():
    """List all todos"""
    print_info('Fetching todos')

    status, data = api_request('/todos', use_auth=True)

    if status == 200 and data:
        print_success(f"Found {len(data)} todos")
        print_json(data)
    else:
        print_error(f"Failed to get todos (HTTP {status})")
        if data:
            print_json(data)
        sys.exit(1)

@todos_group.command(name='get')
@click.argument('todo_id')
def todos_get(todo_id: str):
    """Get a specific todo"""
    print_info(f"Fetching todo: {todo_id}")

    status, data = api_request(f'/todos/{todo_id}', use_auth=True)

    if status == 200 and data:
        print_success('Todo retrieved')
        print_json(data)
    else:
        print_error(f"Failed to get todo (HTTP {status})")
        if data:
            print_json(data)
        sys.exit(1)

@todos_group.command(name='update')
@click.argument('todo_id')
@click.option('--description', help='New description')
@click.option('--priority', type=click.Choice(['low', 'medium', 'high']), help='New priority')
@click.option('--due', help='New due date in ISO format')
def todos_update(todo_id: str, description: Optional[str], priority: Optional[str], due: Optional[str]):
    """Update a todo"""
    print_info(f"Updating todo: {todo_id}")

    updates = {}
    if description:
        updates['description'] = description
    if priority:
        updates['priority'] = priority
    if due:
        updates['dueDate'] = due

    if not updates:
        print_error('No updates specified')
        sys.exit(1)

    status, data = api_request(f'/todos/{todo_id}', 'PATCH', updates, use_auth=True)

    if status == 200 and data:
        print_success('Todo updated')
        print_json(data)
    else:
        print_error(f"Failed to update todo (HTTP {status})")
        if data:
            print_json(data)
        sys.exit(1)

@todos_group.command(name='delete')
@click.argument('todo_id')
def todos_delete(todo_id: str):
    """Delete a todo"""
    print_info(f"Deleting todo: {todo_id}")

    status, data = api_request(f'/todos/{todo_id}', 'DELETE', use_auth=True)

    if status == 204:
        print_success('Todo deleted')
    else:
        print_error(f"Failed to delete todo (HTTP {status})")
        if data:
            print_json(data)
        sys.exit(1)

# Admin user management commands
@cli.group(name='admin')
def admin_group():
    """Admin operations (requires admin/sysadmin role)"""
    pass

@admin_group.command(name='users')
def admin_users():
    """List all users"""
    print_info('Fetching all users (admin)')

    status, data = api_request('/admin/users', use_auth=True)

    if status == 200 and data:
        print_success(f"Found {len(data)} users")
        print_json(data)
    else:
        print_error(f"Failed to get users (HTTP {status})")
        if data:
            print_json(data)
        sys.exit(1)

@admin_group.command(name='users:get')
@click.argument('user_id')
def admin_users_get(user_id: str):
    """Get a specific user"""
    print_info(f"Fetching user: {user_id}")

    status, data = api_request(f'/admin/users/{user_id}', use_auth=True)

    if status == 200 and data:
        print_success('User retrieved')
        print_json(data)
    else:
        print_error(f"Failed to get user (HTTP {status})")
        if data:
            print_json(data)
        sys.exit(1)

@admin_group.command(name='users:update')
@click.argument('user_id')
@click.option('--email', help='New email')
@click.option('--password', help='New password')
@click.option('--full-name', help='New full name')
@click.option('--role', type=click.Choice(['guest', 'admin', 'sysadmin']), help='New role')
@click.option('--email-verified-at', help='Email verified timestamp (empty string, "null", "now", or ISO date)')
def admin_users_update(
    user_id: str,
    email: Optional[str],
    password: Optional[str],
    full_name: Optional[str],
    role: Optional[str],
    email_verified_at: Optional[str]
):
    """Update user (sysadmin only)"""
    print_info(f"Updating user: {user_id}")

    updates = {}
    if email:
        updates['email'] = email
    if password:
        updates['password'] = password
    if full_name:
        updates['fullName'] = full_name
    if role:
        updates['role'] = role
    if email_verified_at is not None:
        updates['emailVerifiedAt'] = email_verified_at

    if not updates:
        print_error('No updates specified')
        sys.exit(1)

    status, data = api_request(f'/admin/users/{user_id}', 'PATCH', updates, use_auth=True)

    if status == 200 and data:
        print_success('User updated')
        print_json(data)
    else:
        print_error(f"Failed to update user (HTTP {status})")
        if data:
            print_json(data)
        sys.exit(1)

@admin_group.command(name='users:delete')
@click.argument('user_id')
def admin_users_delete(user_id: str):
    """Delete user (sysadmin only)"""
    print_info(f"Deleting user: {user_id}")

    status, data = api_request(f'/admin/users/{user_id}', 'DELETE', use_auth=True)

    if status == 204:
        print_success('User deleted')
    else:
        print_error(f"Failed to delete user (HTTP {status})")
        if data:
            print_json(data)
        sys.exit(1)

# Health check commands
@cli.command()
def health():
    """Check API health"""
    print_info('Checking API health')

    status, data = api_request('/health')

    if status == 200 and data:
        print_success('API is healthy')
        print_json(data)
    else:
        print_error(f"API health check failed (HTTP {status})")
        if data:
            print_json(data)
        sys.exit(1)

@cli.command()
def readiness():
    """Check API readiness"""
    print_info('Checking API readiness')

    status, data = api_request('/readiness')

    if status == 200 and data:
        print_success('API is ready')
        print_json(data)
    else:
        print_error(f"API readiness check failed (HTTP {status})")
        if data:
            print_json(data)
        sys.exit(1)

# Token management commands
@cli.group(name='tokens')
def tokens_group():
    """Token management"""
    pass

@tokens_group.command(name='clear')
def tokens_clear():
    """Delete token file"""
    clear_tokens()

if __name__ == '__main__':
    cli()
