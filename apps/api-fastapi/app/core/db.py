"""Database configuration and session management."""

from collections.abc import Generator

from sqlalchemy import Engine
from sqlmodel import Session, create_engine

from app.core.config import settings

_engine: Engine | None = None


def get_engine() -> Engine:
    """Get or create database engine singleton."""
    global _engine
    if _engine is None:
        # Convert DATABASE_URL to use psycopg driver
        db_url = str(settings.db_url)
        if db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
        elif db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)

        _engine = create_engine(
            db_url,
            echo=settings.LOG_LEVEL == "debug",
            pool_pre_ping=True,
        )
    return _engine


# For backwards compatibility
engine = property(lambda self: get_engine())


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.

    Yields:
        Database session that will be automatically closed after use.
    """
    with Session(get_engine()) as session:
        yield session
