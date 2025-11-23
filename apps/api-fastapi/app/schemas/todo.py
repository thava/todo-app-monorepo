"""Todo-related schemas (DTOs)."""

import uuid
from datetime import datetime

from pydantic import Field

from app.models.todo import PriorityEnum
from app.schemas.base import CamelCaseModel


class CreateTodoDto(CamelCaseModel):
    """Create todo request schema - accepts camelCase."""

    description: str = Field(
        description="Description of the todo item",
        examples=["Buy groceries for the week"],
    )
    due_date: datetime | None = Field(  # snake_case in Python, camelCase in API
        default=None,
        description="Due date for the todo item",
        examples=["2025-12-31T23:59:59.000Z"],
    )
    priority: PriorityEnum | None = Field(
        default=None,
        description="Priority level of the todo item",
        examples=["medium"],
    )


class UpdateTodoDto(CamelCaseModel):
    """Update todo request schema - accepts camelCase."""

    description: str | None = Field(
        default=None,
        description="Description of the todo item",
        examples=["Buy groceries for the week"],
    )
    due_date: datetime | None = Field(
        default=None,
        description="Due date for the todo item",
        examples=["2025-12-31T23:59:59.000Z"],
    )
    priority: PriorityEnum | None = Field(
        default=None,
        description="Priority level of the todo item",
        examples=["medium"],
    )


class TodoResponseDto(CamelCaseModel):
    """Todo response schema - auto-converts to camelCase."""

    id: uuid.UUID
    owner_id: uuid.UUID
    description: str
    due_date: datetime | None
    priority: str
    created_at: datetime
    updated_at: datetime
