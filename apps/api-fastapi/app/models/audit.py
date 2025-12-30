"""Audit log model for tracking user actions."""

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, Field, SQLModel


class AuditLog(SQLModel, table=True):
    """Audit log model for tracking user actions."""

    __tablename__ = "audit_logs"  # type: ignore[assignment]

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID | None = Field(default=None, foreign_key="users.id")
    action: str = Field(max_length=100)
    entity_type: str | None = Field(default=None, max_length=50)
    entity_id: uuid.UUID | None = Field(default=None)
    # Use 'meta' as field name since 'metadata' is reserved by SQLAlchemy
    # Map it to 'metadata' column in database
    meta: dict[str, Any] | None = Field(default=None, sa_column=Column("metadata", JSONB))
    ip_address: str | None = Field(default=None, max_length=45)
    user_agent: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
