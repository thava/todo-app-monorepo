"""Todo-related database models."""

import uuid
from datetime import UTC, datetime
from enum import Enum

from sqlmodel import Column, Field, SQLModel  # type: ignore[reportUnknownVariableType]
from sqlmodel import Enum as SQLEnum


class PriorityEnum(str, Enum):
    """Todo priority enumeration."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# Shared properties for Todo model
class TodoBase(SQLModel):
    """Base todo properties shared across Todo table and API schemas."""

    model_config = {"use_enum_values": True}

    description: str
    due_date: datetime | None = Field(default=None)
    priority: PriorityEnum = Field(
        default=PriorityEnum.MEDIUM,
        sa_column=Column(
            SQLEnum(PriorityEnum, values_callable=lambda x: [e.value for e in x]),
            nullable=False,
            server_default="medium"
        )
    )


# Database model - table name explicitly set to match existing schema
class Todo(TodoBase, table=True):
    """Todo model - uses snake_case to follow Python and SQL conventions."""

    __tablename__ = "todos"  # type: ignore[assignment]

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
