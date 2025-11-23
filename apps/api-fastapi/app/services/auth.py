"""Authentication service with user registration, login, and token management."""

import secrets
import uuid
from datetime import datetime, timedelta, timezone
from hashlib import sha256

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.user import (
    EmailVerificationToken,
    PasswordResetToken,
    RefreshTokenSession,
    User,
)
from app.schemas.auth import (
    AuthResponseDto,
    LoginDto,
    RegisterDto,
    RegisteredUserInfo,
    RegisterResponseDto,
    UserInfo,
)
from app.services.jwt import JWTService
from app.services.password import PasswordService


class AuthService:
    """Service for authentication operations."""

    def __init__(
        self,
        session: Session,
        password_service: PasswordService | None = None,
        jwt_service: JWTService | None = None,
    ):
        """Initialize auth service."""
        self.session = session
        self.password_service = password_service or PasswordService()
        self.jwt_service = jwt_service or JWTService()

    def register(
        self, register_dto: RegisterDto, user_agent: str | None = None, ip_address: str | None = None
    ) -> RegisterResponseDto:
        """Register a new user."""
        # Normalize email
        normalized_email = register_dto.email.lower().strip()

        # Validate password strength
        validation = self.password_service.validate_password_strength(
            register_dto.password, normalized_email
        )

        if not validation["isValid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Password does not meet security requirements",
                    "errors": validation["errors"],
                },
            )

        # Check if user already exists
        statement = select(User).where(User.email == normalized_email)
        existing_user = self.session.exec(statement).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )

        # Hash password
        password_hash = self.password_service.hash_password(register_dto.password)

        # Create user with snake_case fields
        new_user = User(
            id=uuid.uuid4(),
            email=normalized_email,
            full_name=register_dto.full_name.strip(),
            password_hash_primary=password_hash,
            role=register_dto.role,
            email_verified_at=datetime.now(timezone.utc) if register_dto.autoverify else None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        self.session.add(new_user)
        self.session.commit()
        self.session.refresh(new_user)

        # TODO: Send verification email if not autoverified

        # DTO will auto-convert to camelCase for API response
        return RegisterResponseDto(
            user=RegisteredUserInfo(
                id=new_user.id,
                email=new_user.email,
                full_name=new_user.full_name,
                role=new_user.role.value,
                email_verified=register_dto.autoverify,
            )
        )

    def login(
        self, login_dto: LoginDto, user_agent: str | None = None, ip_address: str | None = None
    ) -> AuthResponseDto:
        """Login user and return tokens."""
        # Normalize email
        normalized_email = login_dto.email.lower().strip()

        # Find user
        statement = select(User).where(User.email == normalized_email)
        user = self.session.exec(statement).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        # Verify password
        is_valid = self.password_service.verify_password(
            user.password_hash_primary, login_dto.password
        )

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        # Check if email is verified
        if not user.email_verified_at:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please verify your email address before logging in",
            )

        # Generate tokens and create session
        return self._create_auth_response(user, user_agent, ip_address)

    def refresh_access_token(
        self, refresh_token: str, user_agent: str | None = None, ip_address: str | None = None
    ) -> AuthResponseDto:
        """Refresh access token using refresh token."""
        # Verify refresh token
        try:
            payload = self.jwt_service.verify_refresh_token(refresh_token)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        # Hash the refresh token for lookup
        token_hash = self._hash_token(refresh_token)

        # Find session
        statement = select(RefreshTokenSession).where(
            RefreshTokenSession.refresh_token_hash == token_hash
        )
        session_obj = self.session.exec(statement).first()

        if not session_obj:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        # Check if session is revoked
        if session_obj.revoked_at:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked",
            )

        # Check if session is expired
        expires_at = session_obj.expires_at.replace(tzinfo=None) if session_obj.expires_at.tzinfo else session_obj.expires_at
        if datetime.now(timezone.utc) > expires_at:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired",
            )

        # Get user
        user_id = uuid.UUID(payload.get("sub"))
        statement = select(User).where(User.id == user_id)
        user = self.session.exec(statement).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        # Revoke old refresh token (rotation)
        session_obj.revoked_at = datetime.now(timezone.utc)
        self.session.add(session_obj)
        self.session.commit()

        # Generate new tokens and create new session
        return self._create_auth_response(user, user_agent, ip_address)

    def logout(self, refresh_token: str) -> None:
        """Logout by revoking refresh token."""
        token_hash = self._hash_token(refresh_token)

        statement = select(RefreshTokenSession).where(
            RefreshTokenSession.refresh_token_hash == token_hash
        )
        session_obj = self.session.exec(statement).first()

        if session_obj:
            session_obj.revoked_at = datetime.now(timezone.utc)
            self.session.add(session_obj)
            self.session.commit()

    def verify_email(self, token: str) -> dict[str, str | bool]:
        """Verify email with token."""
        token_hash = self._hash_token(token)

        # Find token
        statement = select(EmailVerificationToken).where(
            EmailVerificationToken.token_hash == token_hash
        )
        verification_token = self.session.exec(statement).first()

        if not verification_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token",
            )

        # Check if expired
        expires_at = verification_token.expires_at.replace(tzinfo=None) if verification_token.expires_at.tzinfo else verification_token.expires_at
        if datetime.now(timezone.utc) > expires_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification token has expired",
            )

        # Check if already verified
        if verification_token.verified_at:
            return {
                "message": "Email is already verified",
                "alreadyVerified": True,
            }

        # Mark token as used
        verification_token.verified_at = datetime.now(timezone.utc)
        self.session.add(verification_token)

        # Mark user email as verified
        statement = select(User).where(User.id == verification_token.user_id)
        user = self.session.exec(statement).first()

        if user:
            user.email_verified_at = datetime.now(timezone.utc)
            self.session.add(user)

        self.session.commit()

        return {
            "message": "Email verified successfully",
            "alreadyVerified": False,
        }

    def resend_verification_email(self, user_id: uuid.UUID) -> None:
        """Resend verification email."""
        statement = select(User).where(User.id == user_id)
        user = self.session.exec(statement).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found",
            )

        if user.email_verified_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already verified",
            )

        # Delete old verification tokens
        statement = select(EmailVerificationToken).where(
            EmailVerificationToken.user_id == user_id
        )
        old_tokens = self.session.exec(statement).all()
        for old_token in old_tokens:
            self.session.delete(old_token)

        # TODO: Send new verification email
        self.session.commit()

    def request_password_reset(self, email: str) -> None:
        """Request password reset."""
        normalized_email = email.lower().strip()

        # Find user
        statement = select(User).where(User.email == normalized_email)
        user = self.session.exec(statement).first()

        # Always return success (security best practice)
        if not user:
            return

        # Generate reset token
        token = self._generate_token()
        token_hash = self._hash_token(token)

        # Set expiry (1 hour)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        # Delete old reset tokens
        statement = select(PasswordResetToken).where(PasswordResetToken.user_id == user.id)
        old_tokens = self.session.exec(statement).all()
        for old_token in old_tokens:
            self.session.delete(old_token)

        # Create new token - type: ignore due to SQLModel Field aliases
        reset_token = PasswordResetToken(
            id=uuid.uuid4(),
            user_id=user.id,  # type: ignore
            token_hash=token_hash,  # type: ignore
            expires_at=expires_at,  # type: ignore
            created_at=datetime.now(timezone.utc),  # type: ignore
        )

        self.session.add(reset_token)
        self.session.commit()

        # TODO: Send password reset email

    def reset_password(self, token: str, new_password: str) -> None:
        """Reset password with token."""
        token_hash = self._hash_token(token)

        # Find token
        statement = select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.used_at.is_(None),  # type: ignore[attr-defined]
        )
        reset_token = self.session.exec(statement).first()

        if not reset_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )

        # Check if expired
        expires_at = reset_token.expires_at.replace(tzinfo=None) if reset_token.expires_at.tzinfo else reset_token.expires_at
        if datetime.now(timezone.utc) > expires_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired",
            )

        # Get user
        statement = select(User).where(User.id == reset_token.user_id)
        user = self.session.exec(statement).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found",
            )

        # Validate new password
        validation = self.password_service.validate_password_strength(new_password, user.email)

        if not validation["isValid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Password does not meet security requirements",
                    "errors": validation["errors"],
                },
            )

        # Hash new password
        password_hash = self.password_service.hash_password(new_password)

        # Update user password
        user.password_hash_primary = password_hash
        self.session.add(user)

        # Mark token as used
        reset_token.used_at = datetime.now(timezone.utc)
        self.session.add(reset_token)

        # Revoke all refresh token sessions
        statement = select(RefreshTokenSession).where(RefreshTokenSession.user_id == user.id)
        sessions = self.session.exec(statement).all()
        for session_obj in sessions:
            session_obj.revoked_at = datetime.now(timezone.utc)
            self.session.add(session_obj)

        self.session.commit()

        # TODO: Send password changed confirmation email

    def _create_auth_response(
        self, user: User, user_agent: str | None = None, ip_address: str | None = None
    ) -> AuthResponseDto:
        """Create authentication response with tokens."""
        # Generate access token
        access_token = self.jwt_service.generate_access_token(user.id, user.email, user.role)

        # Create refresh token session - type: ignore due to SQLModel Field aliases
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        session_obj = RefreshTokenSession(
            id=uuid.uuid4(),
            user_id=user.id,  # type: ignore
            refresh_token_hash="",  # type: ignore - Will be updated below
            user_agent=user_agent,  # type: ignore
            ip_address=ip_address,  # type: ignore
            expires_at=expires_at,  # type: ignore
            created_at=datetime.now(timezone.utc),  # type: ignore
        )

        self.session.add(session_obj)
        self.session.flush()

        # Generate refresh token with session ID
        refresh_token = self.jwt_service.generate_refresh_token(user.id, session_obj.id)

        # Update session with hashed refresh token
        session_obj.refresh_token_hash = self._hash_token(refresh_token)
        self.session.add(session_obj)
        self.session.commit()

        return AuthResponseDto(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserInfo(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                role=user.role.value,
                email_verified=bool(user.email_verified_at),
                email_verified_at=user.email_verified_at,
            ),
        )

    def _hash_token(self, token: str) -> str:
        """Hash token for storage (SHA-256)."""
        return sha256(token.encode()).hexdigest()

    def _generate_token(self) -> str:
        """Generate a random token (32 bytes, urlsafe)."""
        return secrets.token_urlsafe(32)
