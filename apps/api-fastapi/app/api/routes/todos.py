"""Todo management routes."""

import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.api.deps.auth import get_current_active_user
from app.core.db import get_db
from app.models.todo import PriorityEnum, Todo
from app.models.user import RoleEnum, User
from app.schemas.todo import CreateTodoDto, TodoResponseDto, UpdateTodoDto

router = APIRouter(prefix="/todos", tags=["todos"])


def _todo_to_response(todo: Todo) -> TodoResponseDto:
    """Convert Todo model to response DTO."""
    return TodoResponseDto(
        id=todo.id,
        ownerId=todo.owner_id,
        description=todo.description,
        dueDate=todo.due_date,
        priority=todo.priority.value,
        createdAt=todo.created_at,
        updatedAt=todo.updated_at,
    )


@router.post("", response_model=TodoResponseDto, status_code=status.HTTP_201_CREATED)
def create_todo(
    create_dto: CreateTodoDto,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_db)],
) -> TodoResponseDto:
    """
    Create a new todo.

    Creates a new todo item for the authenticated user.
    """
    todo = Todo(
        id=uuid.uuid4(),
        owner_id=current_user.id,
        description=create_dto.description,
        due_date=create_dto.dueDate,
        priority=create_dto.priority or PriorityEnum.MEDIUM,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    session.add(todo)
    session.commit()
    session.refresh(todo)

    return _todo_to_response(todo)


@router.get("", response_model=list[TodoResponseDto])
def get_all_todos(
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_db)],
) -> list[TodoResponseDto]:
    """
    Get all todos.

    Retrieves all todos. Regular users see only their own todos,
    while admins and sysadmins see all todos.
    """
    if current_user.role in [RoleEnum.ADMIN, RoleEnum.SYSADMIN]:
        # Admins and sysadmins see all todos
        statement = select(Todo)
    else:
        # Regular users see only their own todos
        statement = select(Todo).where(Todo.owner_id == current_user.id)

    todos = session.exec(statement).all()
    return [_todo_to_response(todo) for todo in todos]


@router.get("/{id}", response_model=TodoResponseDto)
def get_todo(
    id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_db)],
) -> TodoResponseDto:
    """
    Get a todo by ID.

    Retrieves a specific todo by its ID. Regular users can only access their own todos.
    """
    # For non-admin users, only look for their own todos
    if current_user.role in [RoleEnum.ADMIN, RoleEnum.SYSADMIN]:
        statement = select(Todo).where(Todo.id == id)
    else:
        statement = select(Todo).where(Todo.id == id, Todo.owner_id == current_user.id)

    todo = session.exec(statement).first()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    return _todo_to_response(todo)


@router.patch("/{id}", response_model=TodoResponseDto)
def update_todo(
    id: uuid.UUID,
    update_dto: UpdateTodoDto,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_db)],
) -> TodoResponseDto:
    """
    Update a todo.

    Updates a todo by its ID. Regular users can only update their own todos.
    """
    # For non-admin users, only look for their own todos
    if current_user.role in [RoleEnum.ADMIN, RoleEnum.SYSADMIN]:
        statement = select(Todo).where(Todo.id == id)
    else:
        statement = select(Todo).where(Todo.id == id, Todo.owner_id == current_user.id)

    todo = session.exec(statement).first()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    # Update fields
    if update_dto.description is not None:
        todo.description = update_dto.description
    if update_dto.dueDate is not None:
        todo.due_date = update_dto.dueDate
    if update_dto.priority is not None:
        todo.priority = update_dto.priority

    todo.updated_at = datetime.utcnow()

    session.add(todo)
    session.commit()
    session.refresh(todo)

    return _todo_to_response(todo)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_db)],
) -> None:
    """
    Delete a todo.

    Deletes a todo by its ID. Regular users can only delete their own todos.
    """
    # For non-admin users, only look for their own todos
    if current_user.role in [RoleEnum.ADMIN, RoleEnum.SYSADMIN]:
        statement = select(Todo).where(Todo.id == id)
    else:
        statement = select(Todo).where(Todo.id == id, Todo.owner_id == current_user.id)

    todo = session.exec(statement).first()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    session.delete(todo)
    session.commit()
