"""Main API router configuration."""

from fastapi import APIRouter

from app.api.routes import admin, auth, health, oauth, todos, users

api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router)
api_router.include_router(oauth.router)
api_router.include_router(users.router)
api_router.include_router(todos.router)
api_router.include_router(admin.router)
api_router.include_router(health.router)
