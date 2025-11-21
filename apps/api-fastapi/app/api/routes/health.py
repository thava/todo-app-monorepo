"""Health check routes."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlmodel import Session

from app.core.db import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    """
    Health check.

    Basic health check endpoint. Returns OK if the service is running.
    Used for liveness probes in container orchestration.
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/readiness")
def readiness(
    session: Annotated[Session, Depends(get_db)],
) -> dict[str, str | dict[str, str]]:
    """
    Readiness check.

    Readiness check endpoint that verifies database connectivity.
    Returns OK if all dependencies are available. Used for readiness probes
    in container orchestration.
    """
    # Check database connectivity
    db_status = "ok"
    try:
        session.execute(text("SELECT 1"))
    except Exception:
        db_status = "fail"

    overall_status = "ok" if db_status == "ok" else "degraded"

    return {
        "status": overall_status,
        "checks": {
            "database": db_status,
        },
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
