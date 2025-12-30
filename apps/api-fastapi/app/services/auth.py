"""Authentication service with user registration, login, and token management."""

import secrets
import uuid
from datetime import UTC, datetime, timedelta
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
        audit_service: "AuditService | None" = None,
    ):
        """Initialize auth service."""
        from app.services.audit import AuditService

        self.session = session
        self.password_service = password_service or PasswordService()
        self.jwt_service = jwt_service or JWTService()
        self.audit_service = audit_service or AuditService(session)

    def register(
        self, register_dto: RegisterDto, user_agent: str | None = None, ip_address: str | None = None
    ) -> RegisterResponseDto:
        """Register a new user."""
        # Normalize username (will be used as local username)
        normalized_username = register_dto.email.lower().strip()

        # Validate password strength
        validation = self.password_service.validate_password_strength(
            register_dto.password, normalized_username
        )

        if not validation["isValid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Password does not meet security requirements",
                    "errors": validation["errors"],
                },
            )

        # Check if user already exists with this local username
        statement = select(User).where(User.local_username == normalized_username)
        existing_user = self.session.exec(statement).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this username already exists",
            )

        # Hash password
        password_hash = self.password_service.hash_password(register_dto.password)

        # Create user with snake_case fields
        new_user = User(
            id=uuid.uuid4(),
            local_username=normalized_username,
            full_name=register_dto.full_name.strip(),
            local_password_hash=password_hash,
            local_enabled=True,
            role=register_dto.role,
            email_verified_at=datetime.now(UTC) if register_dto.autoverify else None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        self.session.add(new_user)
        self.session.commit()
        self.session.refresh(new_user)

        # Log registration
        self.audit_service.log_auth(
            "REGISTER",
            new_user.id,
            {
                "local_username": new_user.local_username,
                "role": new_user.role.value,
                "autoverified": register_dto.autoverify,
            },
            ip_address,
            user_agent,
        )

        # TODO: Send verification email if not autoverified

        # DTO will auto-convert to camelCase for API response
        return RegisterResponseDto(
            user=RegisteredUserInfo(
                id=new_user.id,
                email=new_user.email or "",  # Uses computed property
                full_name=new_user.full_name,
                role=new_user.role.value,
                email_verified=register_dto.autoverify,
            )
        )

    def login(
        self, login_dto: LoginDto, user_agent: str | None = None, ip_address: str | None = None
    ) -> AuthResponseDto:
        """Login user and return tokens."""
        # Normalize username
        normalized_username = login_dto.email.lower().strip()

        # Find user by local username
        statement = select(User).where(User.local_username == normalized_username)
        user = self.session.exec(statement).first()

        if not user:
            self.audit_service.log_auth(
                "LOGIN_FAILURE",
                None,
                {"local_username": normalized_username, "reason": "user_not_found"},
                ip_address,
                user_agent,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        # Check if local auth is enabled
        if not user.local_enabled:
            self.audit_service.log_auth(
                "LOGIN_FAILURE",
                user.id,
                {"local_username": user.local_username, "reason": "local_auth_disabled"},
                ip_address,
                user_agent,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Local authentication is disabled for this user",
            )

        # Verify password
        if not user.local_password_hash:
            self.audit_service.log_auth(
                "LOGIN_FAILURE",
                user.id,
                {"local_username": user.local_username, "reason": "no_password_set"},
                ip_address,
                user_agent,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        is_valid = self.password_service.verify_password(
            user.local_password_hash, login_dto.password
        )

        if not is_valid:
            self.audit_service.log_auth(
                "LOGIN_FAILURE",
                user.id,
                {"local_username": user.local_username, "reason": "invalid_password"},
                ip_address,
                user_agent,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        # Check if email is verified
        if not user.email_verified_at:
            self.audit_service.log_auth(
                "LOGIN_FAILURE",
                user.id,
                {"local_username": user.local_username, "reason": "email_not_verified"},
                ip_address,
                user_agent,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please verify your email address before logging in",
            )

        # Log successful login
        self.audit_service.log_auth(
            "LOGIN_SUCCESS",
            user.id,
            {"local_username": user.local_username},
            ip_address,
            user_agent,
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
        expires_at = session_obj.expires_at if session_obj.expires_at.tzinfo else session_obj.expires_at.replace(tzinfo=UTC)
        if datetime.now(UTC) > expires_at:
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
        session_obj.revoked_at = datetime.now(UTC)
        self.session.add(session_obj)
        self.session.commit()

        # Log token rotation
        self.audit_service.log_auth(
            "REFRESH_TOKEN_ROTATED",
            user.id,
            {"session_id": str(session_obj.id)},
            ip_address,
            user_agent,
        )

        # Generate new tokens and create new session
        return self._create_auth_response(user, user_agent, ip_address)

    def logout(self, refresh_token: str) -> None:
        """Logout by revoking refresh token."""
        # Extract user_id from token for audit logging
        user_id: uuid.UUID | None = None
        try:
            payload = self.jwt_service.verify_refresh_token(refresh_token)
            user_id = uuid.UUID(payload.get("sub"))
        except Exception:
            pass  # Token might be invalid, but we still try to revoke it

        token_hash = self._hash_token(refresh_token)

        statement = select(RefreshTokenSession).where(
            RefreshTokenSession.refresh_token_hash == token_hash
        )
        session_obj = self.session.exec(statement).first()

        if session_obj:
            session_obj.revoked_at = datetime.now(UTC)
            self.session.add(session_obj)
            self.session.commit()

            # Log logout (no IP/user_agent available in current signature)
            self.audit_service.log_auth(
                "LOGOUT",
                user_id or session_obj.user_id,
                {},
                None,
                None,
            )

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
        expires_at = verification_token.expires_at if verification_token.expires_at.tzinfo else verification_token.expires_at.replace(tzinfo=UTC)
        if datetime.now(UTC) > expires_at:
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
        verification_token.verified_at = datetime.now(UTC)
        self.session.add(verification_token)

        # Mark user email as verified
        statement = select(User).where(User.id == verification_token.user_id)
        user = self.session.exec(statement).first()

        if user:
            user.email_verified_at = datetime.now(UTC)
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
        normalized_username = email.lower().strip()

        # Find user by local username
        statement = select(User).where(User.local_username == normalized_username)
        user = self.session.exec(statement).first()

        # Always return success (security best practice)
        if not user or not user.local_enabled:
            return

        # Generate reset token
        token = self._generate_token()
        token_hash = self._hash_token(token)

        # Set expiry (1 hour)
        expires_at = datetime.now(UTC) + timedelta(hours=1)

        # Delete old reset tokens
        statement = select(PasswordResetToken).where(PasswordResetToken.user_id == user.id)
        old_tokens = self.session.exec(statement).all()
        for old_token in old_tokens:
            self.session.delete(old_token)

        reset_token = PasswordResetToken(
            id=uuid.uuid4(),
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            created_at=datetime.now(UTC),
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
        expires_at = reset_token.expires_at if reset_token.expires_at.tzinfo else reset_token.expires_at.replace(tzinfo=UTC)
        if datetime.now(UTC) > expires_at:
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
        user_email = user.email or ""  # Uses computed property
        validation = self.password_service.validate_password_strength(new_password, user_email)

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
        user.local_password_hash = password_hash
        self.session.add(user)

        # Mark token as used
        reset_token.used_at = datetime.now(UTC)
        self.session.add(reset_token)

        # Revoke all refresh token sessions
        statement = select(RefreshTokenSession).where(RefreshTokenSession.user_id == user.id)
        sessions = self.session.exec(statement).all()
        for session_obj in sessions:
            session_obj.revoked_at = datetime.now(UTC)
            self.session.add(session_obj)

        self.session.commit()

        # TODO: Send password changed confirmation email

    async def login_with_google(
        self,
        google_sub: str,
        google_email: str,
        full_name: str,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> AuthResponseDto:
        """Login or create user via Google OAuth."""
        # Look up user ONLY by google_sub (primary identity)
        statement = select(User).where(User.google_sub == google_sub)
        user = self.session.exec(statement).first()

        if user:
            # User exists - check if email has changed and update if needed
            if user.google_email != google_email:
                user.google_email = google_email
                user.updated_at = datetime.now(UTC)
                self.session.add(user)
                self.session.commit()
                self.session.refresh(user)

                self.audit_service.log_auth(
                    "GOOGLE_EMAIL_UPDATED",
                    user.id,
                    {"old_email": user.google_email, "new_email": google_email},
                    ip_address,
                    user_agent,
                )

            # Log successful login
            self.audit_service.log_auth(
                "GOOGLE_LOGIN_SUCCESS",
                user.id,
                {"google_email": google_email},
                ip_address,
                user_agent,
            )
        else:
            # No existing user with this google_sub - create new user
            user = User(
                id=uuid.uuid4(),
                google_sub=google_sub,
                google_email=google_email,
                full_name=full_name,
                role="guest",  # type: ignore[arg-type]
                email_verified_at=datetime.now(UTC),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )

            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)

            self.audit_service.log_auth(
                "GOOGLE_REGISTER",
                user.id,
                {"google_email": google_email},
                ip_address,
                user_agent,
            )

        return self._create_auth_response(user, user_agent, ip_address)

    async def login_with_microsoft(
        self,
        ms_oid: str,
        ms_tid: str,
        ms_email: str,
        full_name: str,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> AuthResponseDto:
        """Login or create user via Microsoft OAuth."""
        # Look up user ONLY by (ms_tid, ms_oid) tuple (primary identity)
        statement = select(User).where(User.ms_oid == ms_oid, User.ms_tid == ms_tid)
        user = self.session.exec(statement).first()

        if user:
            # User exists - check if email has changed and update if needed
            if user.ms_email != ms_email:
                user.ms_email = ms_email
                user.updated_at = datetime.now(UTC)
                self.session.add(user)
                self.session.commit()
                self.session.refresh(user)

                self.audit_service.log_auth(
                    "MICROSOFT_EMAIL_UPDATED",
                    user.id,
                    {"old_email": user.ms_email, "new_email": ms_email},
                    ip_address,
                    user_agent,
                )

            # Log successful login
            self.audit_service.log_auth(
                "MICROSOFT_LOGIN_SUCCESS",
                user.id,
                {"ms_email": ms_email},
                ip_address,
                user_agent,
            )
        else:
            # No existing user with this (ms_tid, ms_oid) - create new user
            user = User(
                id=uuid.uuid4(),
                ms_oid=uuid.UUID(ms_oid),
                ms_tid=uuid.UUID(ms_tid),
                ms_email=ms_email,
                full_name=full_name,
                role="guest",  # type: ignore[arg-type]
                email_verified_at=datetime.now(UTC),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )

            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)

            self.audit_service.log_auth(
                "MICROSOFT_REGISTER",
                user.id,
                {"ms_email": ms_email},
                ip_address,
                user_agent,
            )

        return self._create_auth_response(user, user_agent, ip_address)

    async def link_google_identity(
        self,
        user_id: uuid.UUID,
        google_sub: str,
        google_email: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        """Link Google identity to an existing user."""
        # Verify user exists
        statement = select(User).where(User.id == user_id)
        user = self.session.exec(statement).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # Check if Google identity is already linked to another user
        statement = select(User).where(User.google_sub == google_sub)
        existing_google_user = self.session.exec(statement).first()

        if existing_google_user and existing_google_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This Google account is already linked to another user",
            )

        # Link Google identity
        user.google_sub = google_sub
        user.google_email = google_email
        if not user.email_verified_at:
            user.email_verified_at = datetime.now(UTC)

        self.session.add(user)
        self.session.commit()

        self.audit_service.log_auth(
            "GOOGLE_LINKED",
            user_id,
            {"google_email": google_email},
            ip_address,
            user_agent,
        )

    async def link_microsoft_identity(
        self,
        user_id: uuid.UUID,
        ms_oid: str,
        ms_tid: str,
        ms_email: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        """Link Microsoft identity to an existing user."""
        # Verify user exists
        statement = select(User).where(User.id == user_id)
        user = self.session.exec(statement).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # Check if Microsoft identity is already linked to another user
        statement = select(User).where(User.ms_oid == ms_oid, User.ms_tid == ms_tid)
        existing_ms_user = self.session.exec(statement).first()

        if existing_ms_user and existing_ms_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This Microsoft account is already linked to another user",
            )

        # Link Microsoft identity
        user.ms_oid = uuid.UUID(ms_oid)
        user.ms_tid = uuid.UUID(ms_tid)
        user.ms_email = ms_email
        if not user.email_verified_at:
            user.email_verified_at = datetime.now(UTC)

        self.session.add(user)
        self.session.commit()

        self.audit_service.log_auth(
            "MICROSOFT_LINKED",
            user_id,
            {"ms_email": ms_email},
            ip_address,
            user_agent,
        )

    async def unlink_google_identity(
        self,
        user_id: uuid.UUID,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        """Unlink Google identity from a user. Requires at least one other identity to remain."""
        statement = select(User).where(User.id == user_id)
        user = self.session.exec(statement).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if not user.google_sub:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Google account is not linked",
            )

        # Check if user has at least one other identity
        has_local_identity = user.local_enabled and user.local_username
        has_microsoft_identity = user.ms_oid and user.ms_tid

        if not has_local_identity and not has_microsoft_identity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot unlink Google account - user must have at least one identity (local or Microsoft)",
            )

        # Store email for audit log
        old_email = user.google_email

        # Unlink Google identity
        user.google_sub = None
        user.google_email = None
        user.updated_at = datetime.now(UTC)

        self.session.add(user)
        self.session.commit()

        self.audit_service.log_auth(
            "GOOGLE_UNLINKED",
            user_id,
            {"google_email": old_email},
            ip_address,
            user_agent,
        )

    async def unlink_microsoft_identity(
        self,
        user_id: uuid.UUID,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        """Unlink Microsoft identity from a user. Requires at least one other identity to remain."""
        statement = select(User).where(User.id == user_id)
        user = self.session.exec(statement).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if not user.ms_oid or not user.ms_tid:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Microsoft account is not linked",
            )

        # Check if user has at least one other identity
        has_local_identity = user.local_enabled and user.local_username
        has_google_identity = user.google_sub

        if not has_local_identity and not has_google_identity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot unlink Microsoft account - user must have at least one identity (local or Google)",
            )

        # Store email for audit log
        old_email = user.ms_email

        # Unlink Microsoft identity
        user.ms_oid = None
        user.ms_tid = None
        user.ms_email = None
        user.updated_at = datetime.now(UTC)

        self.session.add(user)
        self.session.commit()

        self.audit_service.log_auth(
            "MICROSOFT_UNLINKED",
            user_id,
            {"ms_email": old_email},
            ip_address,
            user_agent,
        )

    def _create_auth_response(
        self, user: User, user_agent: str | None = None, ip_address: str | None = None
    ) -> AuthResponseDto:
        """Create authentication response with tokens."""
        # Generate access token
        user_email = user.email or ""  # Uses computed property
        access_token = self.jwt_service.generate_access_token(user.id, user_email, user.role)

        expires_at = datetime.now(UTC) + timedelta(days=7)

        session_obj = RefreshTokenSession(
            id=uuid.uuid4(),
            user_id=user.id,
            refresh_token_hash="",
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=expires_at,
            created_at=datetime.now(UTC),
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
                email=user_email,  # Already resolved above
                full_name=user.full_name,
                role=user.role.value,
                email_verified=bool(user.email_verified_at),
                email_verified_at=user.email_verified_at,
                local_username=user.local_username,
                google_email=user.google_email,
                ms_email=user.ms_email,
            ),
        )

    def _hash_token(self, token: str) -> str:
        """Hash token for storage (SHA-256)."""
        return sha256(token.encode()).hexdigest()

    def _generate_token(self) -> str:
        """Generate a random token (32 bytes, urlsafe)."""
        return secrets.token_urlsafe(32)
