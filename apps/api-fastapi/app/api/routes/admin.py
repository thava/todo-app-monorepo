"""Admin routes for user management."""

import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import Session, select

from app.api.deps.auth import require_role
from app.core.db import get_db
from app.models.user import RoleEnum, User
from app.schemas.user import UpdateUserDto, UserResponseDto
from app.services.audit import AuditService
from app.services.password import PasswordService

router = APIRouter(prefix="/admin", tags=["admin"])


def _user_to_response(user: User) -> UserResponseDto:
    """Convert User model to response DTO."""
    return UserResponseDto(
        id=user.id,
        email=user.email or "",
        full_name=user.full_name,
        role=user.role.value,
        email_verified_at=user.email_verified_at,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.get("/users", response_model=list[UserResponseDto])
def get_all_users(
    _: Annotated[User, Depends(require_role(RoleEnum.ADMIN, RoleEnum.SYSADMIN))],
    session: Annotated[Session, Depends(get_db)],
) -> list[UserResponseDto]:
    """
    Get all users.

    Retrieves all users in the system. Requires admin or sysadmin role.
    """
    statement = select(User)
    users = session.exec(statement).all()
    return [_user_to_response(user) for user in users]


@router.get("/users/{id}", response_model=UserResponseDto)
def get_user_by_id(
    id: uuid.UUID,
    request: Request,
    current_user: Annotated[User, Depends(require_role(RoleEnum.ADMIN, RoleEnum.SYSADMIN))],
    session: Annotated[Session, Depends(get_db)],
) -> UserResponseDto:
    """
    Get user by ID.

    Retrieves a specific user by their ID. Requires admin or sysadmin role.
    """
    statement = select(User).where(User.id == id)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Log admin action
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None
    audit_service = AuditService(session)
    audit_service.log_admin(
        "ADMIN_USER_VIEWED",
        current_user.id,
        "user",
        user.id,
        {"viewed_user_email": user.email or ""},
        ip_address,
        user_agent,
    )

    return _user_to_response(user)


@router.patch("/users/{id}", response_model=UserResponseDto)
def update_user(
    id: uuid.UUID,
    update_dto: UpdateUserDto,
    request: Request,
    current_user: Annotated[User, Depends(require_role(RoleEnum.ADMIN, RoleEnum.SYSADMIN))],
    session: Annotated[Session, Depends(get_db)],
) -> UserResponseDto:
    """
    Update user.

    Updates a user by their ID. Can update email, password, full name, role,
    and email verification status. Requires admin or sysadmin role.
    Admins cannot modify sysadmins or promote users to sysadmin.
    """
    statement = select(User).where(User.id == id)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check if admin is trying to modify a sysadmin
    if current_user.role == RoleEnum.ADMIN and user.role == RoleEnum.SYSADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins cannot modify sysadmin users",
        )

    # Update fields
    if update_dto.email is not None:
        # Check if local username is already taken
        normalized_username = update_dto.email.lower().strip()
        statement = select(User).where(User.local_username == normalized_username, User.id != id)
        existing_user = session.exec(statement).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already in use",
            )
        user.local_username = normalized_username

    if update_dto.password is not None:
        password_service = PasswordService()
        user_email = user.email or ""  # Uses computed property
        validation = password_service.validate_password_strength(update_dto.password, user_email)
        if not validation["isValid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Password does not meet security requirements",
                    "errors": validation["errors"],
                },
            )
        user.local_password_hash = password_service.hash_password(update_dto.password)

    if update_dto.full_name is not None:
        user.full_name = update_dto.full_name

    if update_dto.role is not None:
        try:
            new_role = RoleEnum(update_dto.role)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role: {update_dto.role}",
            )

        # Check if admin is trying to promote to sysadmin
        if current_user.role == RoleEnum.ADMIN and new_role == RoleEnum.SYSADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins cannot promote users to sysadmin role",
            )

        user.role = new_role

    if "email_verified_at" in update_dto.model_fields_set:
        if isinstance(update_dto.email_verified_at, str):
            # Handle "now" as a special value
            if update_dto.email_verified_at.lower() == "now":
                user.email_verified_at = datetime.now(UTC)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid emailVerifiedAt value. Use 'now' or ISO 8601 datetime",
                )
        else:
            # Can be datetime or None
            user.email_verified_at = update_dto.email_verified_at

    user.updated_at = datetime.now(UTC)

    session.add(user)
    session.commit()
    session.refresh(user)

    # Log admin action
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None
    audit_service = AuditService(session)
    audit_service.log_admin(
        "ADMIN_USER_UPDATED",
        current_user.id,
        "user",
        user.id,
        {"updated_fields": list(update_dto.model_fields_set)},
        ip_address,
        user_agent,
    )

    return _user_to_response(user)


@router.delete("/users/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    id: uuid.UUID,
    request: Request,
    current_user: Annotated[User, Depends(require_role(RoleEnum.ADMIN, RoleEnum.SYSADMIN))],
    session: Annotated[Session, Depends(get_db)],
) -> None:
    """
    Delete user.

    Deletes a user by their ID. Requires admin or sysadmin role.
    Admins cannot delete sysadmins.
    """
    statement = select(User).where(User.id == id)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check if admin is trying to delete a sysadmin
    if current_user.role == RoleEnum.ADMIN and user.role == RoleEnum.SYSADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins cannot delete sysadmin users",
        )

    # Prevent deleting yourself
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    # Log admin action before deletion
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None
    audit_service = AuditService(session)
    audit_service.log_admin(
        "ADMIN_USER_DELETED",
        current_user.id,
        "user",
        user.id,
        {"deleted_user_email": user.email or ""},
        ip_address,
        user_agent,
    )

    session.delete(user)
    session.commit()
