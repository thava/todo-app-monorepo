"""User-related database models."""

import uuid
from datetime import datetime
from enum import Enum

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class RoleEnum(str, Enum):
    """User role enumeration."""

    GUEST = "guest"
    ADMIN = "admin"
    SYSADMIN = "sysadmin"


class User(SQLModel, table=True):
    """User model."""

    __tablename__ = "users"  # type: ignore[assignment]

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    full_name: str = Field(alias="fullName", max_length=255)
    password_hash_primary: str = Field(alias="passwordHashPrimary")
    role: RoleEnum = Field(default=RoleEnum.GUEST)
    email_verified_at: datetime | None = Field(
        default=None, alias="emailVerifiedAt"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, alias="createdAt"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, alias="updatedAt"
    )


class RefreshTokenSession(SQLModel, table=True):
    """Refresh token session model."""

    __tablename__ = "refresh_token_sessions"  # type: ignore[assignment]

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", alias="userId")
    refresh_token_hash: str = Field(alias="refreshTokenHash")
    user_agent: str | None = Field(default=None, alias="userAgent")
    ip_address: str | None = Field(default=None, max_length=45, alias="ipAddress")
    expires_at: datetime = Field(alias="expiresAt")
    revoked_at: datetime | None = Field(default=None, alias="revokedAt")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, alias="createdAt"
    )


class PasswordResetToken(SQLModel, table=True):
    """Password reset token model."""

    __tablename__ = "password_reset_tokens"  # type: ignore[assignment]

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", alias="userId")
    token_hash: str = Field(alias="tokenHash")
    expires_at: datetime = Field(alias="expiresAt")
    used_at: datetime | None = Field(default=None, alias="usedAt")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, alias="createdAt"
    )


class EmailVerificationToken(SQLModel, table=True):
    """Email verification token model."""

    __tablename__ = "email_verification_tokens"  # type: ignore[assignment]

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", alias="userId")
    token_hash: str = Field(alias="tokenHash")
    expires_at: datetime = Field(alias="expiresAt")
    verified_at: datetime | None = Field(default=None, alias="verifiedAt")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, alias="createdAt"
    )
