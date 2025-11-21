"""Integration tests for admin endpoints."""

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.user import RoleEnum, User
from tests.conftest import create_test_user


class TestAdminUsers:
    """Test admin user management endpoints."""

    def test_list_users_as_admin(
        self, client: TestClient, admin_token: str, guest_user: User, admin_user: User
    ) -> None:
        """Test that admin can list all users."""
        response = client.get(
            "/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

        user_emails = [user["email"] for user in data]
        assert guest_user.email in user_emails
        assert admin_user.email in user_emails

    def test_list_users_as_guest(self, client: TestClient, guest_token: str) -> None:
        """Test that guest cannot list users."""
        response = client.get(
            "/admin/users",
            headers={"Authorization": f"Bearer {guest_token}"},
        )

        assert response.status_code == 403

    def test_list_users_without_auth(self, client: TestClient) -> None:
        """Test listing users without authentication."""
        response = client.get("/admin/users")
        assert response.status_code == 403

    def test_get_user_by_id_as_admin(
        self, client: TestClient, admin_token: str, guest_user: User
    ) -> None:
        """Test that admin can get user by ID."""
        response = client.get(
            f"/admin/users/{guest_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(guest_user.id)
        assert data["email"] == guest_user.email

    def test_get_user_by_id_as_guest(
        self, client: TestClient, guest_token: str, admin_user: User
    ) -> None:
        """Test that guest cannot get user by ID."""
        response = client.get(
            f"/admin/users/{admin_user.id}",
            headers={"Authorization": f"Bearer {guest_token}"},
        )

        assert response.status_code == 403

    def test_get_nonexistent_user(self, client: TestClient, admin_token: str) -> None:
        """Test getting nonexistent user."""
        from uuid import uuid4

        response = client.get(
            f"/admin/users/{uuid4()}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 404

    def test_update_user_as_admin(
        self, client: TestClient, admin_token: str, guest_user: User
    ) -> None:
        """Test that admin can update user."""
        response = client.patch(
            f"/admin/users/{guest_user.id}",
            json={"fullName": "Updated by Admin"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["fullName"] == "Updated by Admin"

    def test_update_user_role_as_admin(
        self, client: TestClient, admin_token: str, guest_user: User
    ) -> None:
        """Test that admin can update user role."""
        response = client.patch(
            f"/admin/users/{guest_user.id}",
            json={"role": "admin"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "admin"

    def test_admin_cannot_promote_to_sysadmin(
        self, client: TestClient, admin_token: str, guest_user: User
    ) -> None:
        """Test that admin cannot promote user to sysadmin."""
        response = client.patch(
            f"/admin/users/{guest_user.id}",
            json={"role": "sysadmin"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 403
        assert "sysadmin" in response.json()["detail"].lower()

    def test_sysadmin_can_promote_to_sysadmin(
        self, client: TestClient, sysadmin_token: str, guest_user: User
    ) -> None:
        """Test that sysadmin can promote user to sysadmin."""
        response = client.patch(
            f"/admin/users/{guest_user.id}",
            json={"role": "sysadmin"},
            headers={"Authorization": f"Bearer {sysadmin_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "sysadmin"

    def test_admin_cannot_modify_sysadmin(
        self, client: TestClient, admin_token: str, sysadmin_user: User
    ) -> None:
        """Test that admin cannot modify sysadmin."""
        response = client.patch(
            f"/admin/users/{sysadmin_user.id}",
            json={"fullName": "Hacked"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 403
        assert "sysadmin" in response.json()["detail"].lower()

    def test_delete_user_as_admin(
        self,
        client: TestClient,
        admin_token: str,
        session: Session,
        password_service,
    ) -> None:
        """Test that admin can delete user."""
        # Create a user to delete
        user = create_test_user(
            session, password_service, "todelete@example.com", "To Delete", RoleEnum.GUEST
        )

        response = client.delete(
            f"/admin/users/{user.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 204

        # Verify user is deleted
        get_response = client.get(
            f"/admin/users/{user.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert get_response.status_code == 404

    def test_admin_cannot_delete_sysadmin(
        self, client: TestClient, admin_token: str, sysadmin_user: User
    ) -> None:
        """Test that admin cannot delete sysadmin."""
        response = client.delete(
            f"/admin/users/{sysadmin_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 403

    def test_delete_user_as_guest(
        self, client: TestClient, guest_token: str, admin_user: User
    ) -> None:
        """Test that guest cannot delete user."""
        response = client.delete(
            f"/admin/users/{admin_user.id}",
            headers={"Authorization": f"Bearer {guest_token}"},
        )

        assert response.status_code == 403


class TestAdminUserEmailVerification:
    """Test admin email verification management."""

    def test_admin_can_verify_email(
        self,
        client: TestClient,
        admin_token: str,
        session: Session,
        password_service,
    ) -> None:
        """Test that admin can verify user email."""
        # Create unverified user
        user = create_test_user(
            session,
            password_service,
            "unverified@example.com",
            "Unverified",
            verified=False,
        )

        response = client.patch(
            f"/admin/users/{user.id}",
            json={"emailVerifiedAt": "now"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["emailVerifiedAt"] is not None

    def test_admin_can_unverify_email(
        self, client: TestClient, admin_token: str, guest_user: User
    ) -> None:
        """Test that admin can unverify user email."""
        response = client.patch(
            f"/admin/users/{guest_user.id}",
            json={"emailVerifiedAt": None},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["emailVerifiedAt"] is None
