"""Todo-related database models."""

import uuid
from datetime import datetime
from enum import Enum

from sqlmodel import Field, SQLModel


class PriorityEnum(str, Enum):
    """Todo priority enumeration."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Todo(SQLModel, table=True):
    """Todo model."""

    __tablename__ = "todos"  # type: ignore[assignment]

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(foreign_key="users.id", alias="ownerId")
    description: str
    due_date: datetime | None = Field(default=None, alias="dueDate")
    priority: PriorityEnum = Field(default=PriorityEnum.MEDIUM)
    created_at: datetime = Field(
        default_factory=datetime.utcnow, alias="createdAt"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, alias="updatedAt"
    )
