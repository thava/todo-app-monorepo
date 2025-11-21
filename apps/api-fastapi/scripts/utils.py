#!/usr/bin/env python3
"""
CLI Utility for Todo FastAPI

Usage:
    python scripts/utils.py register test@example.com password123 "Test User"
    python scripts/utils.py login test@example.com password123
    python scripts/utils.py todos:create "Buy groceries" --priority=high --due="2025-12-31"
    python scripts/utils.py todos:list
    python scripts/utils.py todos:delete <todo_id>
    python scripts/utils.py db:reinit
    python scripts/utils.py users:list
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv
from sqlalchemy import text
from sqlmodel import Session, create_engine, select

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.models.todo import Todo
from app.models.user import RoleEnum, User
from app.services.password import PasswordService

# Configuration
API_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")
TOKEN_FILE = Path.cwd() / ".dev-tokens.json"
DOMAIN = 'domain.com'

# Colors
class Colors:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"


def print_success(message: str) -> None:
    """Print success message."""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")


def print_error(message: str) -> None:
    """Print error message."""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}", file=sys.stderr)


def print_info(message: str) -> None:
    """Print info message."""
    print(f"{Colors.BLUE}ℹ {message}{Colors.RESET}")


def print_warning(message: str) -> None:
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")


def print_json(data: Any) -> None:
    """Print JSON data."""
    print(json.dumps(data, indent=2, default=str))


# Token management
def save_tokens(access_token: str, refresh_token: str) -> None:
    """Save tokens to file."""
    token_data = {
        "accessToken": access_token,
        "refreshToken": refresh_token,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    TOKEN_FILE.write_text(json.dumps(token_data, indent=2))
    print_success(f"Tokens saved to {TOKEN_FILE}")


def load_tokens() -> dict[str, str] | None:
    """Load tokens from file."""
    if not TOKEN_FILE.exists():
        print_error(f"Token file not found: {TOKEN_FILE}")
        return None

    try:
        tokens = json.loads(TOKEN_FILE.read_text())
        print_success("Tokens loaded")
        return tokens
    except Exception as e:
        print_error(f"Failed to load tokens: {e}")
        return None


def clear_tokens() -> None:
    """Clear token file."""
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()
        print_success("Token file deleted")
    else:
        print_info("No token file to delete")


# HTTP helper
async def api_request(
    endpoint: str,
    method: str = "GET",
    body: dict | None = None,
    auth: bool = False,
) -> dict | None:
    """Make API request."""
    url = f"{API_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}

    if auth:
        tokens = load_tokens()
        if not tokens:
            print_error("No tokens found. Please login first.")
            return None
        headers["Authorization"] = f"Bearer {tokens['accessToken']}"

    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                response = await client.get(url, headers=headers)
            elif method == "POST":
                response = await client.post(url, headers=headers, json=body)
            elif method == "PATCH":
                response = await client.patch(url, headers=headers, json=body)
            elif method == "DELETE":
                response = await client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")

            if response.status_code >= 400:
                print_error(f"API Error ({response.status_code}): {response.text}")
                return None

            if response.status_code == 204:
                return {}

            return response.json()
        except Exception as e:
            print_error(f"Request failed: {e}")
            return None


# Auth commands
async def cmd_register(email: str, password: str, full_name: str, **kwargs: Any) -> None:
    """Register new user."""
    autoverify = kwargs.get("autoverify", False)
    role = kwargs.get("role", "guest")

    body = {
        "email": email,
        "password": password,
        "fullName": full_name,
        "autoverify": autoverify,
        "role": role,
    }

    print_info(f"Registering user: {email}")
    result = await api_request("/auth/register", method="POST", body=body)

    if result:
        print_success("User registered successfully!")
        print_json(result)


async def cmd_login(email: str, password: str) -> None:
    """Login user."""
    body = {"email": email, "password": password}

    print_info(f"Logging in: {email}")
    result = await api_request("/auth/login", method="POST", body=body)

    if result and "accessToken" in result:
        save_tokens(result["accessToken"], result["refreshToken"])
        print_success("Login successful!")
        print_json(result["user"])


async def cmd_logout() -> None:
    """Logout user."""
    tokens = load_tokens()
    if not tokens:
        return

    body = {"refreshToken": tokens["refreshToken"]}
    await api_request("/auth/logout", method="POST", body=body, auth=True)
    clear_tokens()
    print_success("Logged out successfully!")


async def cmd_me() -> None:
    """Get current user profile."""
    result = await api_request("/me", auth=True)
    if result:
        print_json(result)


# Todo commands
async def cmd_todos_list() -> None:
    """List all todos."""
    result = await api_request("/todos", auth=True)
    if result:
        print_info(f"Found {len(result)} todos:")
        print_json(result)


async def cmd_todos_create(description: str, **kwargs: Any) -> None:
    """Create new todo."""
    body: dict[str, Any] = {"description": description}

    if "priority" in kwargs:
        body["priority"] = kwargs["priority"]
    if "due" in kwargs:
        body["dueDate"] = kwargs["due"]

    print_info(f"Creating todo: {description}")
    result = await api_request("/todos", method="POST", body=body, auth=True)

    if result:
        print_success("Todo created successfully!")
        print_json(result)


async def cmd_todos_get(todo_id: str) -> None:
    """Get todo by ID."""
    result = await api_request(f"/todos/{todo_id}", auth=True)
    if result:
        print_json(result)


async def cmd_todos_update(todo_id: str, **kwargs: Any) -> None:
    """Update todo."""
    body: dict[str, Any] = {}

    if "description" in kwargs:
        body["description"] = kwargs["description"]
    if "priority" in kwargs:
        body["priority"] = kwargs["priority"]
    if "due" in kwargs:
        body["dueDate"] = kwargs["due"]

    print_info(f"Updating todo: {todo_id}")
    result = await api_request(f"/todos/{todo_id}", method="PATCH", body=body, auth=True)

    if result:
        print_success("Todo updated successfully!")
        print_json(result)


async def cmd_todos_delete(todo_id: str) -> None:
    """Delete todo."""
    print_info(f"Deleting todo: {todo_id}")
    result = await api_request(f"/todos/{todo_id}", method="DELETE", auth=True)

    if result is not None:
        print_success("Todo deleted successfully!")


# Admin commands
async def cmd_users_list() -> None:
    """List all users (admin only)."""
    result = await api_request("/admin/users", auth=True)
    if result:
        print_info(f"Found {len(result)} users:")
        print_json(result)


async def cmd_users_get(user_id: str) -> None:
    """Get user by ID (admin only)."""
    result = await api_request(f"/admin/users/{user_id}", auth=True)
    if result:
        print_json(result)


# Database commands
def cmd_db_reinit() -> None:
    """Reinitialize database (drop all data and recreate)."""
    print_warning("This will DELETE ALL DATA in the database!")
    confirm = input("Type 'yes' to confirm: ")

    if confirm.lower() != "yes":
        print_info("Aborted")
        return

    # Convert DATABASE_URL to use psycopg driver
    db_url = str(settings.DATABASE_URL)
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

    engine = create_engine(db_url)

    with Session(engine) as session:
        # Drop all tables
        print_info("Dropping all tables...")
        session.execute(text("DROP SCHEMA public CASCADE"))
        session.execute(text("CREATE SCHEMA public"))
        session.commit()
        print_success("All tables dropped")

    # Run migrations
    print_info("Running migrations...")
    os.system("uv run alembic upgrade head")

    # Initialize data
    print_info("Initializing data...")
    os.system("uv run python -m app.initial_data")

    print_success("Database reinitialized!")


def cmd_db_status() -> None:
    """Show database status."""
    # Convert DATABASE_URL to use psycopg driver
    db_url = str(settings.DATABASE_URL)
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

    engine = create_engine(db_url)

    with Session(engine) as session:
        # Count users
        user_count = len(session.exec(select(User)).all())
        todo_count = len(session.exec(select(Todo)).all())

        print_info("Database Status:")
        print(f"  Users: {user_count}")
        print(f"  Todos: {todo_count}")


def cmd_db_seed() -> None:
    """Seed database with demo data."""
    print_info("Seeding database with demo data...")

    # Convert DATABASE_URL to use psycopg driver
    db_url = str(settings.DATABASE_URL)
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

    engine = create_engine(db_url)
    password_service = PasswordService()

    with Session(engine) as session:
        # Create demo users if they don't exist
        demo_users = [
            (f"guest1@{DOMAIN}", "Test User 1", RoleEnum.GUEST),
            (f"admin1@{DOMAIN}", "Admin User", RoleEnum.ADMIN),
        ]

        for email, full_name, role in demo_users:
            existing = session.exec(select(User).where(User.email == email)).first()
            if not existing:
                user = User(
                    email=email,
                    full_name=full_name,
                    password_hash_primary=password_service.hash_password("Todo####"),
                    role=role,
                    email_verified_at=datetime.utcnow(),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                session.add(user)
                print_success(f"Created user: {email}")

        session.commit()

    print_success("Database seeded!")


# Main CLI
async def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Todo FastAPI CLI Utility")
    parser.add_argument("command", help="Command to execute")
    parser.add_argument("args", nargs="*", help="Command arguments")
    parser.add_argument("--priority", choices=["low", "medium", "high"], help="Priority level")
    parser.add_argument("--due", help="Due date (ISO format)")
    parser.add_argument("--description", help="Description")
    parser.add_argument("--autoverify", action="store_true", help="Auto-verify email")
    parser.add_argument("--role", choices=["guest", "admin", "sysadmin"], help="User role")

    args = parser.parse_args()
    command = args.command
    cmd_args = args.args

    # Load environment
    load_dotenv()

    # Route commands
    try:
        if command == "register":
            if len(cmd_args) < 3:
                print_error("Usage: register <email> <password> <full_name>")
                sys.exit(1)
            await cmd_register(
                cmd_args[0],
                cmd_args[1],
                cmd_args[2],
                autoverify=args.autoverify,
                role=args.role or "guest",
            )

        elif command == "login":
            if len(cmd_args) < 2:
                print_error("Usage: login <email> <password>")
                sys.exit(1)
            await cmd_login(cmd_args[0], cmd_args[1])

        elif command == "logout":
            await cmd_logout()

        elif command == "me":
            await cmd_me()

        elif command == "todos:list":
            await cmd_todos_list()

        elif command == "todos:create":
            if len(cmd_args) < 1:
                print_error("Usage: todos:create <description> [--priority=...] [--due=...]")
                sys.exit(1)
            await cmd_todos_create(
                cmd_args[0],
                priority=args.priority,
                due=args.due,
            )

        elif command == "todos:get":
            if len(cmd_args) < 1:
                print_error("Usage: todos:get <todo_id>")
                sys.exit(1)
            await cmd_todos_get(cmd_args[0])

        elif command == "todos:update":
            if len(cmd_args) < 1:
                print_error("Usage: todos:update <todo_id> [--description=...] [--priority=...] [--due=...]")
                sys.exit(1)
            await cmd_todos_update(
                cmd_args[0],
                description=args.description,
                priority=args.priority,
                due=args.due,
            )

        elif command == "todos:delete":
            if len(cmd_args) < 1:
                print_error("Usage: todos:delete <todo_id>")
                sys.exit(1)
            await cmd_todos_delete(cmd_args[0])

        elif command == "users:list":
            await cmd_users_list()

        elif command == "users:get":
            if len(cmd_args) < 1:
                print_error("Usage: users:get <user_id>")
                sys.exit(1)
            await cmd_users_get(cmd_args[0])

        elif command == "db:reinit":
            cmd_db_reinit()

        elif command == "db:status":
            cmd_db_status()

        elif command == "db:seed":
            cmd_db_seed()

        else:
            print_error(f"Unknown command: {command}")
            print_info("Available commands:")
            print("  register, login, logout, me")
            print("  todos:list, todos:create, todos:get, todos:update, todos:delete")
            print("  users:list, users:get")
            print("  db:reinit, db:status, db:seed")
            sys.exit(1)

    except KeyboardInterrupt:
        print_info("\nAborted")
        sys.exit(0)
    except Exception as e:
        print_error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
