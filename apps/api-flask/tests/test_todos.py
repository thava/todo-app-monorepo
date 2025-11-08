"""Tests for Todo CRUD operations"""
import pytest
from datetime import datetime, timedelta


class TestTodoCreate:
    """Test creating todos"""

    def test_create_todo_success(self, client, auth_headers):
        """Test creating a todo successfully"""
        response = client.post('/todos',
            headers=auth_headers,
            json={
                'description': 'Test todo item',
                'priority': 'high'
            }
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data['description'] == 'Test todo item'
        assert data['priority'] == 'high'
        assert 'id' in data
        assert 'ownerId' in data
        assert 'createdAt' in data
        assert 'updatedAt' in data

    def test_create_todo_with_due_date(self, client, auth_headers):
        """Test creating a todo with due date"""
        due_date = (datetime.utcnow() + timedelta(days=7)).isoformat()

        response = client.post('/todos',
            headers=auth_headers,
            json={
                'description': 'Todo with due date',
                'priority': 'medium',
                'dueDate': due_date
            }
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data['description'] == 'Todo with due date'
        assert data['priority'] == 'medium'
        assert data['dueDate'] is not None

    def test_create_todo_minimal(self, client, auth_headers):
        """Test creating a todo with minimal fields"""
        response = client.post('/todos',
            headers=auth_headers,
            json={
                'description': 'Minimal todo'
            }
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data['description'] == 'Minimal todo'
        assert data['priority'] == 'medium'  # Default priority
        assert data['dueDate'] is None

    def test_create_todo_unauthorized(self, client):
        """Test creating a todo without authentication"""
        response = client.post('/todos',
            json={
                'description': 'Unauthorized todo'
            }
        )

        assert response.status_code == 401

    def test_create_todo_missing_description(self, client, auth_headers):
        """Test creating a todo without description"""
        response = client.post('/todos',
            headers=auth_headers,
            json={
                'priority': 'high'
            }
        )

        assert response.status_code == 400

    def test_create_todo_invalid_priority(self, client, auth_headers):
        """Test creating a todo with invalid priority"""
        response = client.post('/todos',
            headers=auth_headers,
            json={
                'description': 'Invalid priority',
                'priority': 'invalid'
            }
        )

        assert response.status_code == 400


class TestTodoRead:
    """Test reading todos"""

    def test_get_all_todos_empty(self, client, auth_headers):
        """Test getting all todos when none exist"""
        response = client.get('/todos', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_all_todos(self, client, auth_headers):
        """Test getting all todos"""
        # Create some todos
        client.post('/todos', headers=auth_headers, json={'description': 'Todo 1'})
        client.post('/todos', headers=auth_headers, json={'description': 'Todo 2'})
        client.post('/todos', headers=auth_headers, json={'description': 'Todo 3'})

        response = client.get('/todos', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 3
        # Should be in descending order (newest first)
        assert data[0]['description'] == 'Todo 3'

    def test_get_own_todos_only(self, client, auth_headers, admin_headers):
        """Test that regular users only see their own todos"""
        # User creates todos
        client.post('/todos', headers=auth_headers, json={'description': 'User todo 1'})
        client.post('/todos', headers=auth_headers, json={'description': 'User todo 2'})

        # Admin creates todos
        client.post('/todos', headers=admin_headers, json={'description': 'Admin todo 1'})

        # User should only see their own todos
        response = client.get('/todos', headers=auth_headers)
        data = response.get_json()
        assert len(data) == 2
        assert all('User todo' in todo['description'] for todo in data)

    def test_admin_sees_all_todos(self, client, auth_headers, admin_headers):
        """Test that admin users see all todos"""
        # User creates todos
        client.post('/todos', headers=auth_headers, json={'description': 'User todo'})

        # Admin creates todos
        client.post('/todos', headers=admin_headers, json={'description': 'Admin todo'})

        # Admin should see all todos
        response = client.get('/todos', headers=admin_headers)
        data = response.get_json()
        assert len(data) == 2

    def test_get_todo_by_id(self, client, auth_headers):
        """Test getting a specific todo by ID"""
        # Create a todo
        create_response = client.post('/todos',
            headers=auth_headers,
            json={'description': 'Specific todo', 'priority': 'high'}
        )
        todo_id = create_response.get_json()['id']

        # Get the todo
        response = client.get(f'/todos/{todo_id}', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == todo_id
        assert data['description'] == 'Specific todo'
        assert data['priority'] == 'high'

    def test_get_todo_not_found(self, client, auth_headers):
        """Test getting a non-existent todo"""
        fake_id = '00000000-0000-0000-0000-000000000000'
        response = client.get(f'/todos/{fake_id}', headers=auth_headers)

        assert response.status_code == 404

    def test_get_other_user_todo_forbidden(self, client, auth_headers, admin_headers):
        """Test that regular users cannot access other users' todos"""
        # Admin creates a todo
        create_response = client.post('/todos',
            headers=admin_headers,
            json={'description': 'Admin todo'}
        )
        todo_id = create_response.get_json()['id']

        # Regular user tries to access it
        response = client.get(f'/todos/{todo_id}', headers=auth_headers)

        assert response.status_code == 403

    def test_get_todos_unauthorized(self, client):
        """Test getting todos without authentication"""
        response = client.get('/todos')

        assert response.status_code == 401


class TestTodoUpdate:
    """Test updating todos"""

    def test_update_todo_description(self, client, auth_headers):
        """Test updating todo description"""
        # Create a todo
        create_response = client.post('/todos',
            headers=auth_headers,
            json={'description': 'Original description'}
        )
        todo_id = create_response.get_json()['id']

        # Update the todo
        response = client.patch(f'/todos/{todo_id}',
            headers=auth_headers,
            json={'description': 'Updated description'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['description'] == 'Updated description'

    def test_update_todo_priority(self, client, auth_headers):
        """Test updating todo priority"""
        # Create a todo
        create_response = client.post('/todos',
            headers=auth_headers,
            json={'description': 'Test todo', 'priority': 'low'}
        )
        todo_id = create_response.get_json()['id']

        # Update priority
        response = client.patch(f'/todos/{todo_id}',
            headers=auth_headers,
            json={'priority': 'high'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['priority'] == 'high'
        # Description should remain unchanged
        assert data['description'] == 'Test todo'

    def test_update_todo_due_date(self, client, auth_headers):
        """Test updating todo due date"""
        # Create a todo
        create_response = client.post('/todos',
            headers=auth_headers,
            json={'description': 'Test todo'}
        )
        todo_id = create_response.get_json()['id']

        # Add due date
        due_date = (datetime.utcnow() + timedelta(days=5)).isoformat()
        response = client.patch(f'/todos/{todo_id}',
            headers=auth_headers,
            json={'dueDate': due_date}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['dueDate'] is not None

    def test_update_todo_multiple_fields(self, client, auth_headers):
        """Test updating multiple fields at once"""
        # Create a todo
        create_response = client.post('/todos',
            headers=auth_headers,
            json={'description': 'Original', 'priority': 'low'}
        )
        todo_id = create_response.get_json()['id']

        # Update multiple fields
        due_date = (datetime.utcnow() + timedelta(days=3)).isoformat()
        response = client.patch(f'/todos/{todo_id}',
            headers=auth_headers,
            json={
                'description': 'Updated',
                'priority': 'high',
                'dueDate': due_date
            }
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['description'] == 'Updated'
        assert data['priority'] == 'high'
        assert data['dueDate'] is not None

    def test_update_todo_not_found(self, client, auth_headers):
        """Test updating a non-existent todo"""
        fake_id = '00000000-0000-0000-0000-000000000000'
        response = client.patch(f'/todos/{fake_id}',
            headers=auth_headers,
            json={'description': 'Updated'}
        )

        assert response.status_code == 404

    def test_update_other_user_todo_forbidden(self, client, auth_headers, admin_headers):
        """Test that regular users cannot update other users' todos"""
        # Admin creates a todo
        create_response = client.post('/todos',
            headers=admin_headers,
            json={'description': 'Admin todo'}
        )
        todo_id = create_response.get_json()['id']

        # Regular user tries to update it
        response = client.patch(f'/todos/{todo_id}',
            headers=auth_headers,
            json={'description': 'Hacked!'}
        )

        assert response.status_code == 403

    def test_sysadmin_can_update_any_todo(self, client, auth_headers, sysadmin_headers):
        """Test that sysadmin can update any todo"""
        # User creates a todo
        create_response = client.post('/todos',
            headers=auth_headers,
            json={'description': 'User todo'}
        )
        todo_id = create_response.get_json()['id']

        # Sysadmin updates it
        response = client.patch(f'/todos/{todo_id}',
            headers=sysadmin_headers,
            json={'description': 'Updated by sysadmin'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['description'] == 'Updated by sysadmin'

    def test_update_todo_invalid_priority(self, client, auth_headers):
        """Test updating with invalid priority"""
        # Create a todo
        create_response = client.post('/todos',
            headers=auth_headers,
            json={'description': 'Test todo'}
        )
        todo_id = create_response.get_json()['id']

        # Try to update with invalid priority
        response = client.patch(f'/todos/{todo_id}',
            headers=auth_headers,
            json={'priority': 'invalid'}
        )

        assert response.status_code == 400


class TestTodoDelete:
    """Test deleting todos"""

    def test_delete_todo_success(self, client, auth_headers):
        """Test deleting a todo successfully"""
        # Create a todo
        create_response = client.post('/todos',
            headers=auth_headers,
            json={'description': 'To be deleted'}
        )
        todo_id = create_response.get_json()['id']

        # Delete the todo
        response = client.delete(f'/todos/{todo_id}', headers=auth_headers)

        assert response.status_code == 204

        # Verify it's deleted
        get_response = client.get(f'/todos/{todo_id}', headers=auth_headers)
        assert get_response.status_code == 404

    def test_delete_todo_not_found(self, client, auth_headers):
        """Test deleting a non-existent todo"""
        fake_id = '00000000-0000-0000-0000-000000000000'
        response = client.delete(f'/todos/{fake_id}', headers=auth_headers)

        assert response.status_code == 404

    def test_delete_other_user_todo_forbidden(self, client, auth_headers, admin_headers):
        """Test that regular users cannot delete other users' todos"""
        # Admin creates a todo
        create_response = client.post('/todos',
            headers=admin_headers,
            json={'description': 'Admin todo'}
        )
        todo_id = create_response.get_json()['id']

        # Regular user tries to delete it
        response = client.delete(f'/todos/{todo_id}', headers=auth_headers)

        assert response.status_code == 403

    def test_sysadmin_can_delete_any_todo(self, client, auth_headers, sysadmin_headers):
        """Test that sysadmin can delete any todo"""
        # User creates a todo
        create_response = client.post('/todos',
            headers=auth_headers,
            json={'description': 'User todo'}
        )
        todo_id = create_response.get_json()['id']

        # Sysadmin deletes it
        response = client.delete(f'/todos/{todo_id}', headers=sysadmin_headers)

        assert response.status_code == 204

    def test_delete_todo_unauthorized(self, client, auth_headers):
        """Test deleting without authentication"""
        # Create a todo first
        create_response = client.post('/todos',
            headers=auth_headers,
            json={'description': 'Test todo'}
        )
        todo_id = create_response.get_json()['id']

        # Try to delete without auth
        response = client.delete(f'/todos/{todo_id}')

        assert response.status_code == 401


class TestTodoOwnership:
    """Test todo ownership and access control"""

    def test_todo_owner_info_included(self, client, auth_headers):
        """Test that owner information is included in todo response"""
        response = client.post('/todos',
            headers=auth_headers,
            json={'description': 'Test todo'}
        )

        assert response.status_code == 201
        data = response.get_json()
        assert 'ownerEmail' in data
        assert 'ownerName' in data
        assert 'ownerRole' in data
        assert data['ownerEmail'] == 'test@example.com'

    def test_multiple_users_separate_todos(self, client, auth_headers, admin_headers):
        """Test that multiple users have separate todo lists"""
        # User creates 2 todos
        client.post('/todos', headers=auth_headers, json={'description': 'User todo 1'})
        client.post('/todos', headers=auth_headers, json={'description': 'User todo 2'})

        # Admin creates 1 todo
        client.post('/todos', headers=admin_headers, json={'description': 'Admin todo 1'})

        # User should see 2 todos
        user_response = client.get('/todos', headers=auth_headers)
        assert len(user_response.get_json()) == 2

        # Admin should see all 3 todos (admin role sees all)
        admin_response = client.get('/todos', headers=admin_headers)
        assert len(admin_response.get_json()) == 3


class TestTodoValidation:
    """Test todo input validation"""

    def test_empty_description_rejected(self, client, auth_headers):
        """Test that empty description is rejected"""
        response = client.post('/todos',
            headers=auth_headers,
            json={'description': ''}
        )

        # Empty string should fail validation
        assert response.status_code in [400, 422]

    def test_very_long_description_accepted(self, client, auth_headers):
        """Test that very long descriptions are accepted"""
        long_desc = 'A' * 5000  # 5000 characters
        response = client.post('/todos',
            headers=auth_headers,
            json={'description': long_desc}
        )

        assert response.status_code == 201

    def test_invalid_date_format(self, client, auth_headers):
        """Test that invalid date format is rejected"""
        response = client.post('/todos',
            headers=auth_headers,
            json={
                'description': 'Test todo',
                'dueDate': 'not-a-date'
            }
        )

        assert response.status_code in [400, 422]

    def test_past_due_date_accepted(self, client, auth_headers):
        """Test that past due dates are accepted (business logic allows it)"""
        past_date = (datetime.utcnow() - timedelta(days=7)).isoformat()
        response = client.post('/todos',
            headers=auth_headers,
            json={
                'description': 'Overdue todo',
                'dueDate': past_date
            }
        )

        # Past dates should be allowed
        assert response.status_code == 201
