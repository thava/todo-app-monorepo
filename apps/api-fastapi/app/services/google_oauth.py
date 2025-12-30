"""Google OAuth service."""

import base64
import json
from typing import TypedDict
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException, status

from app.core.config import settings


class GoogleTokenResponse(TypedDict):
    """Google token response structure."""

    access_token: str
    expires_in: int
    scope: str
    token_type: str
    id_token: str
    refresh_token: str | None


class GoogleUserInfo(TypedDict):
    """Google user information structure."""

    sub: str
    email: str
    email_verified: bool
    name: str
    picture: str | None
    given_name: str | None
    family_name: str | None


class GoogleOAuthService:
    """Service for Google OAuth operations."""

    def __init__(self):
        """Initialize Google OAuth service."""
        self.client_id = settings.GOOGLE_OAUTH_CLIENT_ID
        self.client_secret = settings.GOOGLE_OAUTH_CLIENT_SECRET

        if not self.client_id or not self.client_secret:
            raise ValueError("Google OAuth credentials must be configured")

        self.authorization_endpoint = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_endpoint = "https://oauth2.googleapis.com/token"

    def get_redirect_uri(self) -> str:
        """Get the redirect URI for OAuth callback."""
        api_url = settings.FASTAPI_URL
        return f"{api_url}/oauth/google/callback"

    def get_authorization_url(self, state: str) -> str:
        """Build Google authorization URL."""
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.get_redirect_uri(),
            "scope": "openid profile email",
            "state": state,
            "access_type": "offline",
        }

        return f"{self.authorization_endpoint}?{urlencode(params)}"

    async def exchange_code_for_tokens(self, code: str) -> GoogleTokenResponse:
        """Exchange authorization code for tokens."""
        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.get_redirect_uri(),
            "grant_type": "authorization_code",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_endpoint,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            if response.status_code != 200:
                error_text = response.text
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to exchange code for tokens: {error_text}",
                )

            return response.json()

    def decode_id_token(self, id_token: str) -> GoogleUserInfo:
        """
        Decode and extract Google ID token claims (basic decoding).

        In production, use a library like google-auth for proper verification.
        """
        try:
            parts = id_token.split(".")
            if len(parts) != 3:
                raise ValueError("Invalid ID token format")

            # Decode the payload (second part)
            payload_bytes = parts[1].encode("utf-8")
            # Add padding if necessary
            padding = len(payload_bytes) % 4
            if padding:
                payload_bytes += b"=" * (4 - padding)

            payload = json.loads(base64.urlsafe_b64decode(payload_bytes))

            return {
                "sub": payload["sub"],
                "email": payload["email"],
                "email_verified": payload.get("email_verified", False),
                "name": payload["name"],
                "picture": payload.get("picture"),
                "given_name": payload.get("given_name"),
                "family_name": payload.get("family_name"),
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to decode ID token: {str(e)}",
            )

    async def get_user_info(self, code: str) -> GoogleUserInfo:
        """Get user info from Google OAuth."""
        tokens = await self.exchange_code_for_tokens(code)
        return self.decode_id_token(tokens["id_token"])
