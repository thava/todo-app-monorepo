"""Integration tests for authentication endpoints."""

import uuid
from datetime import datetime

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.user import RoleEnum, User
from app.services.password import PasswordService


class TestAuthRegister:
    """Test user registration."""

    def test_register_success(self, client: TestClient) -> None:
        """Test successful user registration."""
        response = client.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "Password123!",
                "fullName": "New User",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert "user" in data
        user = data["user"]
        assert user["email"] == "newuser@example.com"
        assert user["fullName"] == "New User"
        assert user["role"] == "guest"
        assert user["emailVerified"] is False
        assert "id" in user

    def test_register_with_autoverify(self, client: TestClient) -> None:
        """Test registration with autoverify."""
        response = client.post(
            "/auth/register",
            json={
                "email": "verified@example.com",
                "password": "Password123!",
                "fullName": "Verified User",
                "autoverify": True,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert "user" in data
        assert data["user"]["emailVerified"] is True

    def test_register_duplicate_email(self, client: TestClient, guest_user: User) -> None:
        """Test registration with duplicate email."""
        response = client.post(
            "/auth/register",
            json={
                "email": guest_user.email,
                "password": "Password123!",
                "fullName": "Duplicate User",
            },
        )

        assert response.status_code == 409
        data = response.json()
        assert "detail" in data

    def test_register_invalid_email(self, client: TestClient) -> None:
        """Test registration with invalid email."""
        response = client.post(
            "/auth/register",
            json={
                "email": "invalid-email",
                "password": "Password123!",
                "fullName": "Invalid Email User",
            },
        )

        assert response.status_code == 422

    def test_register_weak_password(self, client: TestClient) -> None:
        """Test registration with weak password."""
        response = client.post(
            "/auth/register",
            json={
                "email": "weakpass@example.com",
                "password": "weak",
                "fullName": "Weak Password User",
            },
        )

        assert response.status_code in [400, 422]
        data = response.json()
        assert "detail" in data


class TestAuthLogin:
    """Test user login."""

    def test_login_success(self, client: TestClient, guest_user: User) -> None:
        """Test successful login."""
        response = client.post(
            "/auth/login",
            json={
                "email": "testguest@example.com",
                "password": "Password123!",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "accessToken" in data
        assert "refreshToken" in data
        assert "user" in data
        assert data["user"]["email"] == guest_user.email

    def test_login_invalid_credentials(self, client: TestClient, guest_user: User) -> None:
        """Test login with invalid credentials."""
        response = client.post(
            "/auth/login",
            json={
                "email": "testguest@example.com",
                "password": "WrongPassword!",
            },
        )

        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, client: TestClient) -> None:
        """Test login with nonexistent user."""
        response = client.post(
            "/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "Password123!",
            },
        )

        assert response.status_code == 401

    def test_login_unverified_email(
        self, client: TestClient, session: Session, password_service: PasswordService
    ) -> None:
        """Test login with unverified email."""
        # Create unverified user
        user = User(
            id=uuid.uuid4(),
            email="unverified@example.com",
            full_name="Unverified User",
            password_hash_primary=password_service.hash_password("Password123!"),
            role=RoleEnum.GUEST,
            email_verified_at=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(user)
        session.commit()

        response = client.post(
            "/auth/login",
            json={
                "email": "unverified@example.com",
                "password": "Password123!",
            },
        )

        assert response.status_code == 403
        assert "verify" in response.json()["detail"].lower()


class TestAuthRefresh:
    """Test token refresh."""

    def test_refresh_token_success(self, client: TestClient, guest_user: User) -> None:
        """Test successful token refresh."""
        # First login
        login_response = client.post(
            "/auth/login",
            json={
                "email": "testguest@example.com",
                "password": "Password123!",
            },
        )
        refresh_token = login_response.json()["refreshToken"]

        # Then refresh
        response = client.post(
            "/auth/refresh",
            json={"refreshToken": refresh_token},
        )

        assert response.status_code == 200
        data = response.json()
        assert "accessToken" in data
        assert "refreshToken" in data
        assert data["refreshToken"] != refresh_token  # Token rotation

    def test_refresh_token_invalid(self, client: TestClient) -> None:
        """Test token refresh with invalid token."""
        response = client.post(
            "/auth/refresh",
            json={"refreshToken": "invalid.token.here"},
        )

        assert response.status_code == 401

    def test_refresh_token_reuse(self, client: TestClient, guest_user: User) -> None:
        """Test that refresh tokens cannot be reused."""
        # Login
        login_response = client.post(
            "/auth/login",
            json={
                "email": "testguest@example.com",
                "password": "Password123!",
            },
        )
        refresh_token = login_response.json()["refreshToken"]

        # First refresh - should succeed
        response1 = client.post(
            "/auth/refresh",
            json={"refreshToken": refresh_token},
        )
        assert response1.status_code == 200

        # Second refresh with same token - should fail
        response2 = client.post(
            "/auth/refresh",
            json={"refreshToken": refresh_token},
        )
        assert response2.status_code == 401


class TestAuthLogout:
    """Test user logout."""

    def test_logout_success(self, client: TestClient, guest_user: User, guest_token: str) -> None:
        """Test successful logout."""
        # First login to get refresh token
        login_response = client.post(
            "/auth/login",
            json={
                "email": "testguest@example.com",
                "password": "Password123!",
            },
        )
        refresh_token = login_response.json()["refreshToken"]

        # Logout
        response = client.post(
            "/auth/logout",
            json={"refreshToken": refresh_token},
            headers={"Authorization": f"Bearer {guest_token}"},
        )

        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"

        # Try to use refresh token - should fail
        refresh_response = client.post(
            "/auth/refresh",
            json={"refreshToken": refresh_token},
        )
        assert refresh_response.status_code == 401

    def test_logout_without_auth(self, client: TestClient) -> None:
        """Test logout without authentication."""
        response = client.post(
            "/auth/logout",
            json={"refreshToken": "some.token.here"},
        )

        assert response.status_code == 403
