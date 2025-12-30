"""User-related database models."""

import uuid
from datetime import UTC, datetime
from enum import Enum

from pydantic import computed_field
from sqlmodel import Column, Field, SQLModel  # type: ignore[reportUnknownVariableType]
from sqlmodel import Enum as SQLEnum


class RoleEnum(str, Enum):
    """User role enumeration."""

    GUEST = "guest"
    ADMIN = "admin"
    SYSADMIN = "sysadmin"

# Shared properties for User model
class UserBase(SQLModel):
    """Base user properties shared across User table and API schemas."""

    # model_config = {"use_enum_values": True}

    full_name: str = Field(max_length=255)
    role: RoleEnum = Field(
        default=RoleEnum.GUEST,
        sa_column=Column(
            SQLEnum(RoleEnum, values_callable=lambda x: [e.value for e in x]),
            nullable=False
        )
    )


# Database model - table name explicitly set to match existing schema
class User(UserBase, table=True):
    """User model - uses snake_case to follow Python and SQL conventions."""

    __tablename__ = "users"  # type: ignore[assignment]

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email_verified_at: datetime | None = Field(default=None)

    # Contact email (for future use)
    contact_email: str | None = Field(default=None)

    # Google identity (optional)
    google_sub: str | None = Field(default=None, unique=True, sa_column_kwargs={"unique": True})
    google_email: str | None = Field(default=None)

    # Microsoft identity (optional)
    ms_oid: uuid.UUID | None = Field(default=None)
    ms_tid: uuid.UUID | None = Field(default=None)
    ms_email: str | None = Field(default=None)

    # Local identity (optional, primarily for dev/test + admin only)
    local_enabled: bool = Field(default=False)
    local_username: str | None = Field(default=None, max_length=255, unique=True, sa_column_kwargs={"unique": True})
    local_password_hash: str | None = Field(default=None)

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @computed_field  # type: ignore[prop-decorator]
    @property
    def email(self) -> str | None:
        """Compute email from available identity providers (for backward compatibility)."""
        return self.local_username or self.google_email or self.ms_email


class RefreshTokenSession(SQLModel, table=True):
    """Refresh token session model."""

    __tablename__ = "refresh_token_sessions"  # type: ignore[assignment]

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    refresh_token_hash: str
    user_agent: str | None = Field(default=None)
    ip_address: str | None = Field(default=None, max_length=45)
    expires_at: datetime
    revoked_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class PasswordResetToken(SQLModel, table=True):
    """Password reset token model."""

    __tablename__ = "password_reset_tokens"  # type: ignore[assignment]

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    token_hash: str
    expires_at: datetime
    used_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class EmailVerificationToken(SQLModel, table=True):
    """Email verification token model."""

    __tablename__ = "email_verification_tokens"  # type: ignore[assignment]

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    token_hash: str
    expires_at: datetime
    verified_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
