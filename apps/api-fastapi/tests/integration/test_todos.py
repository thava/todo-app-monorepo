"""Integration tests for todo endpoints."""

from datetime import datetime, timedelta

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.todo import Todo
from app.models.user import User
from tests.conftest import create_test_todo


class TestTodosList:
    """Test listing todos."""

    def test_list_todos_as_guest(
        self, client: TestClient, guest_user: User, guest_token: str, sample_todo: Todo
    ) -> None:
        """Test that guest users see only their own todos."""
        response = client.get(
            "/todos",
            headers={"Authorization": f"Bearer {guest_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == str(sample_todo.id)
        assert data[0]["ownerId"] == str(guest_user.id)

    def test_list_todos_as_admin(
        self,
        client: TestClient,
        guest_user: User,
        admin_user: User,
        admin_token: str,
        session: Session,
    ) -> None:
        """Test that admin users see all todos."""
        # Create todos for both users
        guest_todo = create_test_todo(session, guest_user.id, "Guest todo")
        admin_todo = create_test_todo(session, admin_user.id, "Admin todo")

        response = client.get(
            "/todos",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2

        todo_ids = [todo["id"] for todo in data]
        assert str(guest_todo.id) in todo_ids
        assert str(admin_todo.id) in todo_ids

    def test_list_todos_without_auth(self, client: TestClient) -> None:
        """Test listing todos without authentication."""
        response = client.get("/todos")
        assert response.status_code == 403


class TestTodosCreate:
    """Test creating todos."""

    def test_create_todo_minimal(self, client: TestClient, guest_token: str) -> None:
        """Test creating todo with minimal fields."""
        response = client.post(
            "/todos",
            json={"description": "New todo"},
            headers={"Authorization": f"Bearer {guest_token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["description"] == "New todo"
        assert data["priority"] == "medium"
        assert data["dueDate"] is None
        assert "id" in data
        assert "ownerId" in data

    def test_create_todo_with_all_fields(self, client: TestClient, guest_token: str) -> None:
        """Test creating todo with all fields."""
        due_date = (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z"

        response = client.post(
            "/todos",
            json={
                "description": "Complete project",
                "priority": "high",
                "dueDate": due_date,
            },
            headers={"Authorization": f"Bearer {guest_token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["description"] == "Complete project"
        assert data["priority"] == "high"
        assert data["dueDate"] is not None

    def test_create_todo_invalid_priority(self, client: TestClient, guest_token: str) -> None:
        """Test creating todo with invalid priority."""
        response = client.post(
            "/todos",
            json={
                "description": "New todo",
                "priority": "invalid",
            },
            headers={"Authorization": f"Bearer {guest_token}"},
        )

        assert response.status_code == 422

    def test_create_todo_without_auth(self, client: TestClient) -> None:
        """Test creating todo without authentication."""
        response = client.post(
            "/todos",
            json={"description": "New todo"},
        )

        assert response.status_code == 403


class TestTodosGet:
    """Test getting a single todo."""

    def test_get_own_todo(
        self, client: TestClient, guest_token: str, sample_todo: Todo
    ) -> None:
        """Test getting own todo."""
        response = client.get(
            f"/todos/{sample_todo.id}",
            headers={"Authorization": f"Bearer {guest_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sample_todo.id)
        assert data["description"] == sample_todo.description

    def test_get_other_user_todo_as_guest(
        self, client: TestClient, admin_user: User, guest_token: str, session: Session
    ) -> None:
        """Test that guest cannot get other user's todo."""
        admin_todo = create_test_todo(session, admin_user.id, "Admin's todo")

        response = client.get(
            f"/todos/{admin_todo.id}",
            headers={"Authorization": f"Bearer {guest_token}"},
        )

        assert response.status_code == 404

    def test_get_other_user_todo_as_admin(
        self, client: TestClient, guest_user: User, admin_token: str, session: Session
    ) -> None:
        """Test that admin can get other user's todo."""
        guest_todo = create_test_todo(session, guest_user.id, "Guest's todo")

        response = client.get(
            f"/todos/{guest_todo.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(guest_todo.id)

    def test_get_nonexistent_todo(self, client: TestClient, guest_token: str) -> None:
        """Test getting nonexistent todo."""
        from uuid import uuid4

        response = client.get(
            f"/todos/{uuid4()}",
            headers={"Authorization": f"Bearer {guest_token}"},
        )

        assert response.status_code == 404


class TestTodosUpdate:
    """Test updating todos."""

    def test_update_own_todo(
        self, client: TestClient, guest_token: str, sample_todo: Todo
    ) -> None:
        """Test updating own todo."""
        response = client.patch(
            f"/todos/{sample_todo.id}",
            json={
                "description": "Updated description",
                "priority": "high",
            },
            headers={"Authorization": f"Bearer {guest_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"
        assert data["priority"] == "high"

    def test_update_todo_partial(
        self, client: TestClient, guest_token: str, sample_todo: Todo
    ) -> None:
        """Test partial update of todo."""
        response = client.patch(
            f"/todos/{sample_todo.id}",
            json={"priority": "low"},
            headers={"Authorization": f"Bearer {guest_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["priority"] == "low"
        assert data["description"] == sample_todo.description  # Unchanged

    def test_update_other_user_todo_as_guest(
        self, client: TestClient, admin_user: User, guest_token: str, session: Session
    ) -> None:
        """Test that guest cannot update other user's todo."""
        admin_todo = create_test_todo(session, admin_user.id, "Admin's todo")

        response = client.patch(
            f"/todos/{admin_todo.id}",
            json={"description": "Hacked!"},
            headers={"Authorization": f"Bearer {guest_token}"},
        )

        assert response.status_code == 404

    def test_update_other_user_todo_as_admin(
        self, client: TestClient, guest_user: User, admin_token: str, session: Session
    ) -> None:
        """Test that admin can update other user's todo."""
        guest_todo = create_test_todo(session, guest_user.id, "Guest's todo")

        response = client.patch(
            f"/todos/{guest_todo.id}",
            json={"description": "Admin updated"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Admin updated"


class TestTodosDelete:
    """Test deleting todos."""

    def test_delete_own_todo(
        self, client: TestClient, guest_token: str, sample_todo: Todo
    ) -> None:
        """Test deleting own todo."""
        response = client.delete(
            f"/todos/{sample_todo.id}",
            headers={"Authorization": f"Bearer {guest_token}"},
        )

        assert response.status_code == 204

        # Verify todo is deleted
        get_response = client.get(
            f"/todos/{sample_todo.id}",
            headers={"Authorization": f"Bearer {guest_token}"},
        )
        assert get_response.status_code == 404

    def test_delete_other_user_todo_as_guest(
        self, client: TestClient, admin_user: User, guest_token: str, session: Session
    ) -> None:
        """Test that guest cannot delete other user's todo."""
        admin_todo = create_test_todo(session, admin_user.id, "Admin's todo")

        response = client.delete(
            f"/todos/{admin_todo.id}",
            headers={"Authorization": f"Bearer {guest_token}"},
        )

        assert response.status_code == 404

    def test_delete_other_user_todo_as_admin(
        self, client: TestClient, guest_user: User, admin_token: str, session: Session
    ) -> None:
        """Test that admin can delete other user's todo."""
        guest_todo = create_test_todo(session, guest_user.id, "Guest's todo")

        response = client.delete(
            f"/todos/{guest_todo.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 204

    def test_delete_nonexistent_todo(self, client: TestClient, guest_token: str) -> None:
        """Test deleting nonexistent todo."""
        from uuid import uuid4

        response = client.delete(
            f"/todos/{uuid4()}",
            headers={"Authorization": f"Bearer {guest_token}"},
        )

        assert response.status_code == 404
