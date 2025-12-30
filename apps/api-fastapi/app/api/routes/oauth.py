"""OAuth routes for Google and Microsoft authentication."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.api.deps.auth import get_current_user_id
from app.core.db import get_db
from app.services.auth import AuthService
from app.services.google_oauth import GoogleOAuthService
from app.services.microsoft_oauth import MicrosoftOAuthService
from app.services.oauth_state import OAuthStateService

router = APIRouter(prefix="/oauth", tags=["oauth"])


# Google OAuth endpoints
@router.get("/google/login")
async def google_login(
    redirect: str = Query(..., description="Frontend redirect URL"),
    frontend: str = Query(..., description="Frontend identifier"),
) -> RedirectResponse:
    """
    Initiate Google OAuth login flow.

    Redirects to Google OAuth authorization endpoint.
    """
    oauth_state_service = OAuthStateService()
    google_oauth_service = GoogleOAuthService()

    state = oauth_state_service.create_state(
        redirect=redirect,
        frontend=frontend,
        mode="login",
    )

    authorization_url = google_oauth_service.get_authorization_url(state)
    return RedirectResponse(url=authorization_url, status_code=status.HTTP_302_FOUND)


@router.post("/google/link")
async def google_link(
    redirect: str,
    frontend: str,
    access_token: str,
) -> RedirectResponse:
    """
    Initiate Google OAuth account linking flow.

    Redirects to Google OAuth to link Google account to current user.
    Requires access_token in request body.
    """
    from app.services.jwt import JWTService

    jwt_service = JWTService()

    # Verify the access token and extract user ID
    try:
        payload = jwt_service.verify_access_token(access_token)
        user_id = payload.get("sub")
    except Exception:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        )

    oauth_state_service = OAuthStateService()
    google_oauth_service = GoogleOAuthService()

    state = oauth_state_service.create_state(
        redirect=redirect,
        frontend=frontend,
        mode="link",
        current_user_id=user_id,
    )

    authorization_url = google_oauth_service.get_authorization_url(state)
    return RedirectResponse(url=authorization_url, status_code=status.HTTP_302_FOUND)


@router.get("/google/callback")
async def google_callback(
    code: str = Query(..., description="Authorization code from Google"),
    state: str = Query(..., description="State parameter"),
    request: Request = None,
    session: Session = Depends(get_db),
) -> RedirectResponse:
    """
    Google OAuth callback endpoint.

    Handles the OAuth callback from Google.
    """
    # Default redirect URL in case state is invalid
    redirect_url = "http://localhost:4000/auth-complete"

    try:
        oauth_state_service = OAuthStateService()
        google_oauth_service = GoogleOAuthService()
        auth_service = AuthService(session)

        user_agent = request.headers.get("user-agent") if request else None
        ip_address = request.client.host if request and request.client else None

        state_data = oauth_state_service.verify_state(state)
        redirect_url = state_data["redirect"]

        google_user_info = await google_oauth_service.get_user_info(code)

        if state_data["mode"] == "login":
            auth_response = await auth_service.login_with_google(
                google_user_info["sub"],
                google_user_info["email"],
                google_user_info["name"],
                user_agent,
                ip_address,
            )

            redirect_url = (
                f"{state_data['redirect']}#access_token={auth_response.access_token}"
                f"&refresh_token={auth_response.refresh_token}"
            )
            return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)

        elif state_data["mode"] == "link":
            if not state_data.get("current_user_id"):
                from fastapi import HTTPException

                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User ID required for account linking",
                )

            await auth_service.link_google_identity(
                uuid.UUID(state_data["current_user_id"]),
                google_user_info["sub"],
                google_user_info["email"],
                ip_address,
                user_agent,
            )

            redirect_url = f"{state_data['redirect']}#status=linked&provider=google"
            return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)

    except Exception as error:
        # Always redirect to frontend with error information
        error_code = getattr(error, "status_code", 500)
        error_message = str(error) or "OAuth authentication failed"
        from urllib.parse import quote

        encoded_message = quote(error_message)

        redirect_url = f"{redirect_url}#error={error_code}&message={encoded_message}"
        return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)


# Microsoft OAuth endpoints
@router.get("/microsoft/login")
async def microsoft_login(
    redirect: str = Query(..., description="Frontend redirect URL"),
    frontend: str = Query(..., description="Frontend identifier"),
) -> RedirectResponse:
    """
    Initiate Microsoft OAuth login flow.

    Redirects to Microsoft OAuth authorization endpoint.
    """
    oauth_state_service = OAuthStateService()
    microsoft_oauth_service = MicrosoftOAuthService()

    state = oauth_state_service.create_state(
        redirect=redirect,
        frontend=frontend,
        mode="login",
    )

    authorization_url = microsoft_oauth_service.get_authorization_url(state)
    return RedirectResponse(url=authorization_url, status_code=status.HTTP_302_FOUND)


@router.post("/microsoft/link")
async def microsoft_link(
    redirect: str,
    frontend: str,
    access_token: str,
) -> RedirectResponse:
    """
    Initiate Microsoft OAuth account linking flow.

    Redirects to Microsoft OAuth to link Microsoft account to current user.
    Requires access_token in request body.
    """
    from app.services.jwt import JWTService

    jwt_service = JWTService()

    # Verify the access token and extract user ID
    try:
        payload = jwt_service.verify_access_token(access_token)
        user_id = payload.get("sub")
    except Exception:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        )

    oauth_state_service = OAuthStateService()
    microsoft_oauth_service = MicrosoftOAuthService()

    state = oauth_state_service.create_state(
        redirect=redirect,
        frontend=frontend,
        mode="link",
        current_user_id=user_id,
    )

    authorization_url = microsoft_oauth_service.get_authorization_url(state)
    return RedirectResponse(url=authorization_url, status_code=status.HTTP_302_FOUND)


@router.get("/microsoft/callback")
async def microsoft_callback(
    code: str = Query(..., description="Authorization code from Microsoft"),
    state: str = Query(..., description="State parameter"),
    request: Request = None,
    session: Session = Depends(get_db),
) -> RedirectResponse:
    """
    Microsoft OAuth callback endpoint.

    Handles the OAuth callback from Microsoft.
    """
    # Default redirect URL in case state is invalid
    redirect_url = "http://localhost:4000/auth-complete"

    try:
        oauth_state_service = OAuthStateService()
        microsoft_oauth_service = MicrosoftOAuthService()
        auth_service = AuthService(session)

        user_agent = request.headers.get("user-agent") if request else None
        ip_address = request.client.host if request and request.client else None

        state_data = oauth_state_service.verify_state(state)
        redirect_url = state_data["redirect"]

        ms_user_info = await microsoft_oauth_service.get_user_info(code)

        if state_data["mode"] == "login":
            auth_response = await auth_service.login_with_microsoft(
                ms_user_info["oid"],
                ms_user_info["tid"],
                ms_user_info["email"],
                ms_user_info["name"],
                user_agent,
                ip_address,
            )

            redirect_url = (
                f"{state_data['redirect']}#access_token={auth_response.access_token}"
                f"&refresh_token={auth_response.refresh_token}"
            )
            return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)

        elif state_data["mode"] == "link":
            if not state_data.get("current_user_id"):
                from fastapi import HTTPException

                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User ID required for account linking",
                )

            await auth_service.link_microsoft_identity(
                uuid.UUID(state_data["current_user_id"]),
                ms_user_info["oid"],
                ms_user_info["tid"],
                ms_user_info["email"],
                ip_address,
                user_agent,
            )

            redirect_url = f"{state_data['redirect']}#status=linked&provider=microsoft"
            return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)

    except Exception as error:
        # Always redirect to frontend with error information
        error_code = getattr(error, "status_code", 500)
        error_message = str(error) or "OAuth authentication failed"
        from urllib.parse import quote

        encoded_message = quote(error_message)

        redirect_url = f"{redirect_url}#error={error_code}&message={encoded_message}"
        return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)


# Unlink endpoints
@router.post("/google/unlink", status_code=status.HTTP_204_NO_CONTENT)
async def unlink_google(
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    request: Request,
    session: Annotated[Session, Depends(get_db)],
) -> None:
    """
    Unlink Google account from current user.

    Removes Google identity from current user account.
    Requires at least one other identity to remain.
    """
    auth_service = AuthService(session)
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None

    await auth_service.unlink_google_identity(
        uuid.UUID(current_user_id),
        ip_address,
        user_agent,
    )


@router.post("/microsoft/unlink", status_code=status.HTTP_204_NO_CONTENT)
async def unlink_microsoft(
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    request: Request,
    session: Annotated[Session, Depends(get_db)],
) -> None:
    """
    Unlink Microsoft account from current user.

    Removes Microsoft identity from current user account.
    Requires at least one other identity to remain.
    """
    auth_service = AuthService(session)
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None

    await auth_service.unlink_microsoft_identity(
        uuid.UUID(current_user_id),
        ip_address,
        user_agent,
    )
