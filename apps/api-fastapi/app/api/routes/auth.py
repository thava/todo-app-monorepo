"""Authentication routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from sqlmodel import Session

from app.api.deps.auth import get_current_active_user, get_current_user
from app.core.db import get_db
from app.models.user import User
from app.schemas.auth import (
    AuthResponseDto,
    LoginDto,
    RefreshTokenDto,
    RegisterDto,
    RegisterResponseDto,
    RequestPasswordResetDto,
    ResetPasswordDto,
)
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponseDto, status_code=status.HTTP_201_CREATED)
def register(
    register_dto: RegisterDto,
    request: Request,
    session: Annotated[Session, Depends(get_db)],
) -> RegisterResponseDto:
    """
    Register a new user.

    Creates a new user account. By default, email verification is required.
    """
    auth_service = AuthService(session)
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None

    return auth_service.register(register_dto, user_agent, ip_address)


@router.post("/login", response_model=AuthResponseDto)
def login(
    login_dto: LoginDto,
    request: Request,
    session: Annotated[Session, Depends(get_db)],
) -> AuthResponseDto:
    """
    Login user.

    Authenticates a user and returns access and refresh tokens.
    """
    auth_service = AuthService(session)
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None

    return auth_service.login(login_dto, user_agent, ip_address)


@router.post("/refresh", response_model=AuthResponseDto)
def refresh(
    refresh_dto: RefreshTokenDto,
    request: Request,
    session: Annotated[Session, Depends(get_db)],
) -> AuthResponseDto:
    """
    Refresh access token.

    Generates a new access token using a valid refresh token.
    """
    auth_service = AuthService(session)
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None

    return auth_service.refresh_access_token(refresh_dto.refresh_token, user_agent, ip_address)


@router.post("/logout")
def logout(
    refresh_dto: RefreshTokenDto,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_db)],
) -> dict[str, str]:
    """
    Logout user.

    Invalidates the refresh token and logs out the user.
    """
    auth_service = AuthService(session)
    auth_service.logout(refresh_dto.refresh_token)
    return {"message": "Logged out successfully"}


@router.get("/verify-email")
def verify_email(
    token: str,
    session: Annotated[Session, Depends(get_db)],
) -> dict[str, str | bool]:
    """
    Verify email address.

    Verifies user email using the token sent via email.
    """
    auth_service = AuthService(session)
    return auth_service.verify_email(token)


@router.post("/resend-verification")
def resend_verification(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db)],
) -> dict[str, str]:
    """
    Resend verification email.

    Sends a new email verification link to the authenticated user.
    """
    auth_service = AuthService(session)
    auth_service.resend_verification_email(current_user.id)
    return {"message": "Verification email sent"}


@router.post("/request-password-reset")
def request_password_reset(
    reset_dto: RequestPasswordResetDto,
    session: Annotated[Session, Depends(get_db)],
) -> dict[str, str]:
    """
    Request password reset.

    Sends a password reset link to the provided email address if it exists.
    """
    auth_service = AuthService(session)
    auth_service.request_password_reset(reset_dto.email)
    return {"message": "Password reset request processed"}


@router.post("/reset-password")
def reset_password(
    reset_dto: ResetPasswordDto,
    session: Annotated[Session, Depends(get_db)],
) -> dict[str, str]:
    """
    Reset password.

    Resets user password using the token received via email.
    """
    auth_service = AuthService(session)
    auth_service.reset_password(reset_dto.token, reset_dto.new_password)
    return {"message": "Password reset successfully"}
