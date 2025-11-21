"""Todo-related schemas (DTOs)."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.todo import PriorityEnum


class CreateTodoDto(BaseModel):
    """Create todo request schema."""

    description: str = Field(
        description="Description of the todo item",
        examples=["Buy groceries for the week"],
    )
    dueDate: datetime | None = Field(
        default=None,
        description="Due date for the todo item",
        examples=["2025-12-31T23:59:59.000Z"],
    )
    priority: PriorityEnum | None = Field(
        default=None,
        description="Priority level of the todo item",
        examples=["medium"],
    )


class UpdateTodoDto(BaseModel):
    """Update todo request schema."""

    description: str | None = Field(
        default=None,
        description="Description of the todo item",
        examples=["Buy groceries for the week"],
    )
    dueDate: datetime | None = Field(
        default=None,
        description="Due date for the todo item",
        examples=["2025-12-31T23:59:59.000Z"],
    )
    priority: PriorityEnum | None = Field(
        default=None,
        description="Priority level of the todo item",
        examples=["medium"],
    )


class TodoResponseDto(BaseModel):
    """Todo response schema."""

    id: uuid.UUID
    ownerId: uuid.UUID
    description: str
    dueDate: datetime | None
    priority: str
    createdAt: datetime
    updatedAt: datetime
