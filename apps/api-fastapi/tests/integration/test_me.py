"""Integration tests for /me endpoints (user profile)."""

from fastapi.testclient import TestClient

from app.models.user import User


class TestMeProfile:
    """Test user profile endpoints."""

    def test_get_profile(self, client: TestClient, guest_user: User, guest_token: str) -> None:
        """Test getting own profile."""
        response = client.get(
            "/me",
            headers={"Authorization": f"Bearer {guest_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(guest_user.id)
        assert data["email"] == guest_user.email
        assert data["fullName"] == guest_user.full_name
        assert data["role"] == guest_user.role.value
        assert "passwordHashPrimary" not in data  # Sensitive data excluded

    def test_get_profile_without_auth(self, client: TestClient) -> None:
        """Test getting profile without authentication."""
        response = client.get("/me")
        assert response.status_code == 403

    def test_update_profile(self, client: TestClient, guest_token: str) -> None:
        """Test updating own profile."""
        response = client.patch(
            "/me",
            json={"fullName": "Updated Name"},
            headers={"Authorization": f"Bearer {guest_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["fullName"] == "Updated Name"

    def test_update_email(self, client: TestClient, guest_token: str) -> None:
        """Test updating email (should reset verification)."""
        response = client.patch(
            "/me",
            json={"email": "newemail@example.com"},
            headers={"Authorization": f"Bearer {guest_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newemail@example.com"
        # Email verification should be reset
        assert data["emailVerifiedAt"] is None

    def test_update_to_existing_email(
        self, client: TestClient, guest_token: str, admin_user: User
    ) -> None:
        """Test updating email to one that's already taken."""
        response = client.patch(
            "/me",
            json={"email": admin_user.email},
            headers={"Authorization": f"Bearer {guest_token}"},
        )

        assert response.status_code == 400
        assert "already in use" in response.json()["detail"].lower()

    def test_change_password(self, client: TestClient, guest_token: str) -> None:
        """Test changing password."""
        response = client.patch(
            "/me/password",
            json={
                "currentPassword": "Password123!",
                "newPassword": "NewPassword456!",
            },
            headers={"Authorization": f"Bearer {guest_token}"},
        )

        assert response.status_code == 200
        assert "success" in response.json()["message"].lower()

        # Try logging in with new password
        login_response = client.post(
            "/auth/login",
            json={
                "email": "testguest@example.com",
                "password": "NewPassword456!",
            },
        )
        assert login_response.status_code == 200

    def test_change_password_wrong_current(self, client: TestClient, guest_token: str) -> None:
        """Test changing password with wrong current password."""
        response = client.patch(
            "/me/password",
            json={
                "currentPassword": "WrongPassword!",
                "newPassword": "NewPassword456!",
            },
            headers={"Authorization": f"Bearer {guest_token}"},
        )

        assert response.status_code == 400
        assert "incorrect" in response.json()["detail"].lower()

    def test_change_password_weak_new(self, client: TestClient, guest_token: str) -> None:
        """Test changing password to a weak password."""
        response = client.patch(
            "/me/password",
            json={
                "currentPassword": "Password123!",
                "newPassword": "weak",
            },
            headers={"Authorization": f"Bearer {guest_token}"},
        )

        assert response.status_code in [400, 422]
        # Response could be from Pydantic validation or our custom validation
        response_json = response.json()
        detail_text = str(response_json).lower()
        assert "password" in detail_text or "string" in detail_text

    def test_delete_account(self, client: TestClient, guest_token: str) -> None:
        """Test deleting own account."""
        response = client.delete(
            "/me",
            headers={"Authorization": f"Bearer {guest_token}"},
        )

        assert response.status_code == 204

        # Try to get profile - should fail
        get_response = client.get(
            "/me",
            headers={"Authorization": f"Bearer {guest_token}"},
        )
        assert get_response.status_code == 401
