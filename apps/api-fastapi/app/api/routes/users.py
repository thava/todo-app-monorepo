"""User management routes (/me endpoints)."""

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.api.deps.auth import get_current_active_user
from app.core.db import get_db
from app.models.user import User
from app.schemas.auth import UserInfo
from app.schemas.user import ChangePasswordDto, UpdateProfileDto
from app.services.password import PasswordService

router = APIRouter(prefix="/me", tags=["me"])


@router.get("", response_model=UserInfo)
def get_profile(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserInfo:
    """
    Get current user profile.

    Retrieves the profile of the authenticated user.
    """
    return UserInfo(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role.value,
        email_verified=bool(current_user.email_verified_at),
        email_verified_at=current_user.email_verified_at,
    )


@router.patch("", response_model=UserInfo)
def update_profile(
    update_dto: UpdateProfileDto,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_db)],
) -> UserInfo:
    """
    Update current user profile.

    Updates the profile of the authenticated user.
    """
    if update_dto.email is not None:
        # Check if email is already in use
        statement = select(User).where(User.email == update_dto.email)
        existing_user = session.exec(statement).first()
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already in use",
            )

        current_user.email = update_dto.email
        # Reset email verification when email changes
        current_user.email_verified_at = None

    if update_dto.full_name is not None:
        current_user.full_name = update_dto.full_name

    current_user.updated_at = datetime.now(timezone.utc)

    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return UserInfo(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role.value,
        email_verified=bool(current_user.email_verified_at),
        email_verified_at=current_user.email_verified_at,
    )


@router.patch("/password")
def change_password(
    change_dto: ChangePasswordDto,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_db)],
) -> dict[str, str]:
    """
    Change password.

    Changes the password of the authenticated user.
    """
    password_service = PasswordService()

    # Refetch user from session to ensure we have latest data
    statement = select(User).where(User.id == current_user.id)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Verify current password
    if not password_service.verify_password(
        user.password_hash_primary,
        change_dto.current_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    # Validate new password strength
    if len(change_dto.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters",
        )

    # Hash and update password
    user.password_hash_primary = password_service.hash_password(change_dto.new_password)
    user.updated_at = datetime.now(timezone.utc)

    session.add(user)
    session.commit()

    return {"message": "Password changed successfully"}


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_db)],
) -> None:
    """
    Delete account.

    Deletes the account of the authenticated user.
    """
    session.delete(current_user)
    session.commit()
