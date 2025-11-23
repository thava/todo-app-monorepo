"""User-related database models."""

import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlmodel import Field, SQLModel  # type: ignore[reportUnknownVariableType]


class RoleEnum(str, Enum):
    """User role enumeration."""

    GUEST = "guest"
    ADMIN = "admin"
    SYSADMIN = "sysadmin"


class User(SQLModel, table=True):
    """User model - uses snake_case to follow Python and SQL conventions."""

    __tablename__ = "users"  # type: ignore[assignment]

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    full_name: str = Field(max_length=255)
    password_hash_primary: str
    role: RoleEnum = Field(
        default=RoleEnum.GUEST,
        # SQLAlchemy enum requires values_callable - type stubs incomplete
        sa_column=Column(SQLAlchemyEnum(RoleEnum, values_callable=lambda x: [e.value for e in x]))  # type: ignore[reportUnknownLambdaType, reportUnknownMemberType, reportUnknownVariableType]
    )
    email_verified_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PasswordResetToken(SQLModel, table=True):
    """Password reset token model."""

    __tablename__ = "password_reset_tokens"  # type: ignore[assignment]

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    token_hash: str
    expires_at: datetime
    used_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EmailVerificationToken(SQLModel, table=True):
    """Email verification token model."""

    __tablename__ = "email_verification_tokens"  # type: ignore[assignment]

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    token_hash: str
    expires_at: datetime
    verified_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
