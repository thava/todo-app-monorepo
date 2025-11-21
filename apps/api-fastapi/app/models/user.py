"""User-related database models."""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Column
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlmodel import Field, SQLModel


class RoleEnum(str, Enum):
    """User role enumeration."""

    GUEST = "guest"
    ADMIN = "admin"
    SYSADMIN = "sysadmin"


class User(SQLModel, table=True):
    """User model."""

    __tablename__ = "users"  # type: ignore[assignment]

    model_config = {"populate_by_name": True}  # type: ignore[assignment]

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    full_name: str = Field(alias="fullName", max_length=255, sa_column_kwargs={"name": "fullName"})
    password_hash_primary: str = Field(alias="passwordHashPrimary", sa_column_kwargs={"name": "passwordHashPrimary"})
    role: RoleEnum = Field(
        default=RoleEnum.GUEST,
        sa_column=Column(SQLAlchemyEnum(RoleEnum, values_callable=lambda x: [e.value for e in x]))
    )
    email_verified_at: datetime | None = Field(
        default=None, alias="emailVerifiedAt", sa_column_kwargs={"name": "emailVerifiedAt"}
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, alias="createdAt", sa_column_kwargs={"name": "createdAt"}
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, alias="updatedAt", sa_column_kwargs={"name": "updatedAt"}
    )


class RefreshTokenSession(SQLModel, table=True):
    """Refresh token session model."""

    __tablename__ = "refresh_token_sessions"  # type: ignore[assignment]

    model_config = {"populate_by_name": True}  # type: ignore[assignment]

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", alias="userId", sa_column_kwargs={"name": "userId"})
    refresh_token_hash: str = Field(alias="refreshTokenHash", sa_column_kwargs={"name": "refreshTokenHash"})
    user_agent: str | None = Field(default=None, alias="userAgent", sa_column_kwargs={"name": "userAgent"})
    ip_address: str | None = Field(default=None, max_length=45, alias="ipAddress", sa_column_kwargs={"name": "ipAddress"})
    expires_at: datetime = Field(alias="expiresAt", sa_column_kwargs={"name": "expiresAt"})
    revoked_at: datetime | None = Field(default=None, alias="revokedAt", sa_column_kwargs={"name": "revokedAt"})
    created_at: datetime = Field(
        default_factory=datetime.utcnow, alias="createdAt", sa_column_kwargs={"name": "createdAt"}
    )


class PasswordResetToken(SQLModel, table=True):
    """Password reset token model."""

    __tablename__ = "password_reset_tokens"  # type: ignore[assignment]

    model_config = {"populate_by_name": True}  # type: ignore[assignment]

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", alias="userId", sa_column_kwargs={"name": "userId"})
    token_hash: str = Field(alias="tokenHash", sa_column_kwargs={"name": "tokenHash"})
    expires_at: datetime = Field(alias="expiresAt", sa_column_kwargs={"name": "expiresAt"})
    used_at: datetime | None = Field(default=None, alias="usedAt", sa_column_kwargs={"name": "usedAt"})
    created_at: datetime = Field(
        default_factory=datetime.utcnow, alias="createdAt", sa_column_kwargs={"name": "createdAt"}
    )


class EmailVerificationToken(SQLModel, table=True):
    """Email verification token model."""

    __tablename__ = "email_verification_tokens"  # type: ignore[assignment]

    model_config = {"populate_by_name": True}  # type: ignore[assignment]

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", alias="userId", sa_column_kwargs={"name": "userId"})
    token_hash: str = Field(alias="tokenHash", sa_column_kwargs={"name": "tokenHash"})
    expires_at: datetime = Field(alias="expiresAt", sa_column_kwargs={"name": "expiresAt"})
    verified_at: datetime | None = Field(default=None, alias="verifiedAt", sa_column_kwargs={"name": "verifiedAt"})
    created_at: datetime = Field(
        default_factory=datetime.utcnow, alias="createdAt", sa_column_kwargs={"name": "createdAt"}
    )
