"""User-related schemas (DTOs)."""

import uuid
from datetime import datetime

from pydantic import Field

from app.schemas.base import CamelCaseModel


class UpdateProfileDto(CamelCaseModel):
    """Update profile request schema - uses snake_case internally, accepts/returns camelCase."""

    email: str | None = Field(
        default=None,
        description="User email address",
        examples=["user@example.com"],
    )
    full_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="User full name",
        examples=["Jane Smith"],
    )


class ChangePasswordDto(CamelCaseModel):
    """Change password request schema - uses snake_case internally, accepts/returns camelCase."""

    current_password: str = Field(
        description="Current password",
        examples=["oldPassword123!"],
    )
    new_password: str = Field(
        min_length=8,
        max_length=128,
        description="New password (minimum 8 characters)",
        examples=["newPassword456!"],
    )


class UserResponseDto(CamelCaseModel):
    """User response schema for admin endpoints - auto-converts to camelCase."""

    id: uuid.UUID = Field(description="User ID", examples=["uuid-123"])
    email: str = Field(description="User email address", examples=["user@example.com"])
    full_name: str = Field(description="User full name", examples=["John Doe"])
    role: str = Field(description="User role", examples=["guest"])
    email_verified_at: datetime | None = Field(
        description="Email verification timestamp",
        examples=["2025-01-01T00:00:00.000Z"],
    )
    created_at: datetime = Field(
        description="User creation timestamp",
        examples=["2025-01-01T00:00:00.000Z"],
    )
    updated_at: datetime = Field(
        description="User last update timestamp",
        examples=["2025-01-01T00:00:00.000Z"],
    )


class UpdateUserDto(CamelCaseModel):
    """Update user request schema (admin only) - uses snake_case internally, accepts/returns camelCase."""

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
    full_name: str | None = Field(
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
    email_verified_at: datetime | str | None = Field(
        default=None,
        description="Email verification timestamp (ISO 8601 format, 'now' for current time, or null to unverify)",
        examples=["2025-01-01T00:00:00.000Z", "now"],
    )
