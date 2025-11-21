"""Main FastAPI application."""

import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings


def custom_generate_unique_id(route: APIRoute) -> str:
    """Generate unique operation IDs for OpenAPI schema."""
    if route.tags:
        return f"{route.tags[0]}-{route.name}"
    return route.name


# Initialize Sentry if configured
if settings.SENTRY_DSN and settings.NODE_ENV != "development":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    description="REST API for Todo Application with authentication and role-based access control",
    version="1.0",
)

# Configure CORS
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API router
app.include_router(api_router)


@app.get("/", tags=["App"])
async def root() -> dict[str, str]:
    """Root endpoint - Hello World."""
    return {"message": "Todo App API"}
