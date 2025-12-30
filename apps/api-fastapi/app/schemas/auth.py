"""Authentication-related schemas (DTOs)."""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.user import RoleEnum
from app.schemas.base import CamelCaseModel


class RegisterDto(CamelCaseModel):
    """Registration request schema - accepts and returns camelCase."""

    email: EmailStr = Field(description="User email address", examples=["newuser@example.com"])
    password: str = Field(
        min_length=8,
        max_length=128,
        description="User password (minimum 8 characters)",
        examples=["securePassword123"],
    )
    full_name: str = Field(  # snake_case in Python, camelCase in API
        min_length=1,
        max_length=255,
        description="User full name",
        examples=["John Doe"],
    )
    autoverify: bool = Field(
        default=False,
        description="Auto-verify email (for testing purposes)",
        examples=[False],
    )
    role: RoleEnum = Field(
        default=RoleEnum.GUEST,
        description="User role",
        examples=["guest"],
    )


class RegisteredUserInfo(CamelCaseModel):
    """Registered user information - auto-converts to camelCase."""

    id: uuid.UUID = Field(description="User ID", examples=["uuid-123"])
    email: str = Field(description="User email", examples=["newuser@example.com"])
    full_name: str = Field(description="User full name", examples=["John Doe"])
    role: str = Field(description="User role", examples=["guest"])
    email_verified: bool = Field(description="Email verification status", examples=[False])


class RegisterResponseDto(BaseModel):
    """Registration response schema."""

    user: RegisteredUserInfo = Field(description="Registered user information")


class LoginDto(BaseModel):
    """Login request schema."""

    email: EmailStr = Field(description="User email address", examples=["user@example.com"])
    password: str = Field(description="User password", examples=["securePassword123"])


class UserInfo(CamelCaseModel):
    """User information in auth response - auto-converts to camelCase."""

    id: uuid.UUID = Field(description="User ID", examples=["uuid-123"])
    email: str = Field(description="User email", examples=["user@example.com"])
    full_name: str = Field(description="User full name", examples=["John Doe"])
    role: str = Field(description="User role", examples=["guest"])
    email_verified: bool = Field(description="Email verification status", examples=[True])
    email_verified_at: datetime | None = Field(
        default=None,
        description="Email verification timestamp",
        examples=["2025-01-01T00:00:00.000Z"],
    )
    local_username: str | None = Field(
        default=None,
        description="Local username (if local identity exists)",
        examples=["john.doe"],
    )
    google_email: str | None = Field(
        default=None,
        description="Google email (if Google identity exists)",
        examples=["user@gmail.com"],
    )
    ms_email: str | None = Field(
        default=None,
        description="Microsoft email (if Microsoft identity exists)",
        examples=["user@outlook.com"],
    )


class AuthResponseDto(CamelCaseModel):
    """Authentication response with tokens - auto-converts to camelCase."""

    access_token: str = Field(
        description="JWT access token",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    refresh_token: str = Field(
        description="JWT refresh token",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    user: UserInfo = Field(description="User information")


class RefreshTokenDto(CamelCaseModel):
    """Refresh token request schema - accepts camelCase."""

    refresh_token: str = Field(
        description="Refresh token received from login or previous refresh",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )


class RequestPasswordResetDto(BaseModel):
    """Password reset request schema."""

    email: EmailStr = Field(
        description="Email address to send password reset link",
        examples=["user@example.com"],
    )


class ResetPasswordDto(CamelCaseModel):
    """Password reset schema - accepts camelCase."""

    token: str = Field(
        description="Password reset token received via email",
        examples=["abc123def456"],
    )
    new_password: str = Field(
        min_length=8,
        description="New password (minimum 8 characters)",
        examples=["newSecurePassword123"],
    )
