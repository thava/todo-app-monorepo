"""JWT token generation and verification service."""

import uuid
from datetime import datetime, timedelta

import jwt

from app.core.config import settings
from app.models.user import RoleEnum


def parse_time_string(time_str: str) -> timedelta:
    """
    Parse time string like '15m', '7d', '24h' into timedelta.

    Args:
        time_str: Time string (e.g., '15m', '7d', '24h')

    Returns:
        timedelta object
    """
    unit = time_str[-1]
    value = int(time_str[:-1])

    if unit == "s":
        return timedelta(seconds=value)
    elif unit == "m":
        return timedelta(minutes=value)
    elif unit == "h":
        return timedelta(hours=value)
    elif unit == "d":
        return timedelta(days=value)
    else:
        raise ValueError(f"Invalid time unit: {unit}")


class JWTService:
    """Service for JWT token generation and verification."""

    def __init__(self) -> None:
        """Initialize JWT service with secrets from settings."""
        self.access_secret = settings.JWT_ACCESS_SECRET
        self.refresh_secret = settings.JWT_REFRESH_SECRET
        self.access_expiry = parse_time_string(settings.JWT_ACCESS_EXPIRY)
        self.refresh_expiry = parse_time_string(settings.JWT_REFRESH_EXPIRY)
        self.algorithm = "HS256"

    def generate_access_token(
        self, user_id: uuid.UUID, email: str, role: RoleEnum
    ) -> str:
        """
        Generate access token for user.

        Args:
            user_id: User ID
            email: User email
            role: User role

        Returns:
            JWT access token
        """
        now = datetime.utcnow()
        payload = {
            "sub": str(user_id),
            "email": email,
            "role": role.value,
            "iat": now,
            "exp": now + self.access_expiry,
        }
        return jwt.encode(payload, self.access_secret, algorithm=self.algorithm)

    def generate_refresh_token(
        self, user_id: uuid.UUID, session_id: uuid.UUID
    ) -> str:
        """
        Generate refresh token for user session.

        Args:
            user_id: User ID
            session_id: Session ID

        Returns:
            JWT refresh token
        """
        now = datetime.utcnow()
        payload = {
            "sub": str(user_id),
            "sessionId": str(session_id),
            "iat": now,
            "exp": now + self.refresh_expiry,
        }
        return jwt.encode(payload, self.refresh_secret, algorithm=self.algorithm)

    def verify_access_token(self, token: str) -> dict[str, str]:
        """
        Verify and decode access token.

        Args:
            token: JWT access token

        Returns:
            Decoded token payload

        Raises:
            jwt.ExpiredSignatureError: If token is expired
            jwt.InvalidTokenError: If token is invalid
        """
        payload = jwt.decode(
            token, self.access_secret, algorithms=[self.algorithm]
        )
        return payload

    def verify_refresh_token(self, token: str) -> dict[str, str]:
        """
        Verify and decode refresh token.

        Args:
            token: JWT refresh token

        Returns:
            Decoded token payload

        Raises:
            jwt.ExpiredSignatureError: If token is expired
            jwt.InvalidTokenError: If token is invalid
        """
        payload = jwt.decode(
            token, self.refresh_secret, algorithms=[self.algorithm]
        )
        return payload
