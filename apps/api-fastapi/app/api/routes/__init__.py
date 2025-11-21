"""API routes."""

from app.api.routes import admin, auth, health, todos, users

__all__ = ["auth", "users", "todos", "admin", "health"]
