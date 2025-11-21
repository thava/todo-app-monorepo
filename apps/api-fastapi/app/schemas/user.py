"""User-related schemas (DTOs)."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class UpdateProfileDto(BaseModel):
    """Update profile request schema."""

    email: str | None = Field(
        default=None,
        description="User email address",
        examples=["user@example.com"],
    )
    fullName: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="User full name",
        examples=["Jane Smith"],
    )


class ChangePasswordDto(BaseModel):
    """Change password request schema."""

    currentPassword: str = Field(
        description="Current password",
        examples=["oldPassword123!"],
    )
    newPassword: str = Field(
        min_length=8,
        max_length=128,
        description="New password (minimum 8 characters)",
        examples=["newPassword456!"],
    )


class UserResponseDto(BaseModel):
    """User response schema for admin endpoints."""

    id: uuid.UUID = Field(description="User ID", examples=["uuid-123"])
    email: str = Field(description="User email address", examples=["user@example.com"])
    fullName: str = Field(description="User full name", examples=["John Doe"])
    role: str = Field(description="User role", examples=["guest"])
    emailVerifiedAt: datetime | None = Field(
        description="Email verification timestamp",
        examples=["2025-01-01T00:00:00.000Z"],
    )
    createdAt: datetime = Field(
        description="User creation timestamp",
        examples=["2025-01-01T00:00:00.000Z"],
    )
    updatedAt: datetime = Field(
        description="User last update timestamp",
        examples=["2025-01-01T00:00:00.000Z"],
    )


class UpdateUserDto(BaseModel):
    """Update user request schema (admin only)."""

    email: str | None = Field(
        default=None,
        description="User email address",
        examples=["user@example.com"],
    )
    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=128,
        description="User password (minimum 8 characters)",
        examples=["newPassword123"],
    )
    fullName: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="User full name",
        examples=["John Doe"],
    )
    role: str | None = Field(
        default=None,
        description="User role",
        examples=["guest"],
    )
    emailVerifiedAt: datetime | str | None = Field(
        default=None,
        description="Email verification timestamp (ISO 8601 format, 'now' for current time, or null to unverify)",
        examples=["2025-01-01T00:00:00.000Z", "now"],
    )
