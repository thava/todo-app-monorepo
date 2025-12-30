"""Microsoft OAuth service."""

import base64
import json
from typing import TypedDict
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException, status

from app.core.config import settings


class MicrosoftTokenResponse(TypedDict):
    """Microsoft token response structure."""

    access_token: str
    expires_in: int
    scope: str
    token_type: str
    id_token: str
    refresh_token: str | None


class MicrosoftUserInfo(TypedDict):
    """Microsoft user information structure."""

    oid: str
    tid: str
    sub: str
    email: str
    name: str
    preferred_username: str | None


class MicrosoftOAuthService:
    """Service for Microsoft OAuth operations."""

    def __init__(self):
        """Initialize Microsoft OAuth service."""
        self.client_id = settings.MS_OAUTH_CLIENT_ID
        self.client_secret = settings.MS_OAUTH_CLIENT_SECRET

        if not self.client_id or not self.client_secret:
            raise ValueError("Microsoft OAuth credentials must be configured")

        self.authorization_endpoint = (
            "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
        )
        self.token_endpoint = "https://login.microsoftonline.com/common/oauth2/v2.0/token"

    def get_redirect_uri(self) -> str:
        """Get the redirect URI for OAuth callback."""
        api_url = settings.FASTAPI_URL
        return f"{api_url}/oauth/microsoft/callback"

    def get_authorization_url(self, state: str) -> str:
        """Build Microsoft authorization URL."""
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.get_redirect_uri(),
            "scope": "openid profile email",
            "state": state,
            "response_mode": "query",
        }

        return f"{self.authorization_endpoint}?{urlencode(params)}"

    async def exchange_code_for_tokens(self, code: str) -> MicrosoftTokenResponse:
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

    def decode_id_token(self, id_token: str) -> MicrosoftUserInfo:
        """
        Decode and extract Microsoft ID token claims (basic decoding).

        In production, use a library like msal for proper verification.
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
                "oid": payload["oid"],
                "tid": payload["tid"],
                "sub": payload["sub"],
                "email": payload.get("email") or payload.get("preferred_username", ""),
                "name": payload["name"],
                "preferred_username": payload.get("preferred_username"),
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to decode ID token: {str(e)}",
            )

    async def get_user_info(self, code: str) -> MicrosoftUserInfo:
        """Get user info from Microsoft OAuth."""
        tokens = await self.exchange_code_for_tokens(code)
        return self.decode_id_token(tokens["id_token"])
