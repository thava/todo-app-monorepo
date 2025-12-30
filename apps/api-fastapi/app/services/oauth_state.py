"""OAuth state management service."""

import time
from typing import Literal, TypedDict

import jwt
from fastapi import HTTPException, status

from app.core.config import settings


class OAuthState(TypedDict):
    """OAuth state payload structure."""

    redirect: str
    frontend: str
    mode: Literal["login", "link"]
    current_user_id: str | None
    iat: int
    exp: int


class OAuthStateService:
    """Service for creating and verifying OAuth state parameters."""

    def __init__(self):
        """Initialize OAuth state service."""
        self.state_secret = settings.API_SERVER_OAUTH_KEY
        if not self.state_secret:
            raise ValueError("API_SERVER_OAUTH_KEY must be configured for OAuth")
        self.state_expiry_seconds = 300  # 5 minutes

    def create_state(
        self,
        redirect: str,
        frontend: str,
        mode: Literal["login", "link"],
        current_user_id: str | None = None,
    ) -> str:
        """Create a signed OAuth state parameter."""
        now = int(time.time())

        payload: OAuthState = {
            "redirect": redirect,
            "frontend": frontend,
            "mode": mode,
            "current_user_id": current_user_id,
            "iat": now,
            "exp": now + self.state_expiry_seconds,
        }

        return jwt.encode(payload, self.state_secret, algorithm="HS256")

    def verify_state(self, state: str) -> OAuthState:
        """Verify and decode OAuth state parameter."""
        try:
            decoded = jwt.decode(state, self.state_secret, algorithms=["HS256"])
            return decoded  # type: ignore[return-value]
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OAuth state has expired",
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OAuth state",
            )
