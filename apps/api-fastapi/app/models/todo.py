"""Todo-related database models."""

import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlmodel import Field, SQLModel  # type: ignore[reportUnknownVariableType]


class PriorityEnum(str, Enum):
    """Todo priority enumeration."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Todo(SQLModel, table=True):
    """Todo model - uses snake_case to follow Python and SQL conventions."""

    __tablename__ = "todos"  # type: ignore[assignment]

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(foreign_key="users.id")
    description: str
    due_date: datetime | None = Field(default=None)
    priority: PriorityEnum = Field(
        default=PriorityEnum.MEDIUM,
        # SQLAlchemy enum requires values_callable - type stubs incomplete
        sa_column=Column(SQLAlchemyEnum(PriorityEnum, values_callable=lambda x: [e.value for e in x]))  # type: ignore[reportUnknownLambdaType, reportUnknownMemberType, reportUnknownVariableType]
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
