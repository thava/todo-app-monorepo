"""Authentication-related schemas (DTOs)."""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.user import RoleEnum


class RegisterDto(BaseModel):
    """Registration request schema."""

    email: EmailStr = Field(description="User email address", examples=["newuser@example.com"])
    password: str = Field(
        min_length=8,
        max_length=128,
        description="User password (minimum 8 characters)",
        examples=["securePassword123"],
    )
    fullName: str = Field(
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


class RegisteredUserInfo(BaseModel):
    """Registered user information."""

    id: uuid.UUID = Field(description="User ID", examples=["uuid-123"])
    email: str = Field(description="User email", examples=["newuser@example.com"])
    fullName: str = Field(description="User full name", examples=["John Doe"])
    role: str = Field(description="User role", examples=["guest"])
    emailVerified: bool = Field(description="Email verification status", examples=[False])


class RegisterResponseDto(BaseModel):
    """Registration response schema."""

    user: RegisteredUserInfo = Field(description="Registered user information")


class LoginDto(BaseModel):
    """Login request schema."""

    email: EmailStr = Field(description="User email address", examples=["user@example.com"])
    password: str = Field(description="User password", examples=["securePassword123"])


class UserInfo(BaseModel):
    """User information in auth response."""

    id: uuid.UUID = Field(description="User ID", examples=["uuid-123"])
    email: str = Field(description="User email", examples=["user@example.com"])
    fullName: str = Field(description="User full name", examples=["John Doe"])
    role: str = Field(description="User role", examples=["guest"])
    emailVerified: bool = Field(description="Email verification status", examples=[True])
    emailVerifiedAt: datetime | None = Field(
        default=None,
        description="Email verification timestamp",
        examples=["2025-01-01T00:00:00.000Z"],
    )


class AuthResponseDto(BaseModel):
    """Authentication response with tokens."""

    accessToken: str = Field(
        description="JWT access token",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    refreshToken: str = Field(
        description="JWT refresh token",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    user: UserInfo = Field(description="User information")


class RefreshTokenDto(BaseModel):
    """Refresh token request schema."""

    refreshToken: str = Field(
        description="Refresh token received from login or previous refresh",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )


class RequestPasswordResetDto(BaseModel):
    """Password reset request schema."""

    email: EmailStr = Field(
        description="Email address to send password reset link",
        examples=["user@example.com"],
    )


class ResetPasswordDto(BaseModel):
    """Password reset schema."""

    token: str = Field(
        description="Password reset token received via email",
        examples=["abc123def456"],
    )
    newPassword: str = Field(
        min_length=8,
        description="New password (minimum 8 characters)",
        examples=["newSecurePassword123"],
    )
