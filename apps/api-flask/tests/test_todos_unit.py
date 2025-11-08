"""
Unit tests for Todo operations (without database)

These tests mock the database layer and test business logic only.
They can run without PostgreSQL.
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import uuid


class TestTodoValidationLogic:
    """Test todo validation logic without database"""

    def test_priority_values(self):
        """Test valid priority values"""
        from src.models.todo import PriorityEnum

        assert PriorityEnum.low.value == 'low'
        assert PriorityEnum.medium.value == 'medium'
        assert PriorityEnum.high.value == 'high'

    def test_priority_enum_members(self):
        """Test priority enum has expected members"""
        from src.models.todo import PriorityEnum

        priorities = [p.value for p in PriorityEnum]
        assert 'low' in priorities
        assert 'medium' in priorities
        assert 'high' in priorities
        assert len(priorities) == 3


class TestUserRoleLogic:
    """Test user role logic without database"""

    def test_role_values(self):
        """Test valid role values"""
        from src.models.user import RoleEnum

        assert RoleEnum.guest.value == 'guest'
        assert RoleEnum.admin.value == 'admin'
        assert RoleEnum.sysadmin.value == 'sysadmin'

    def test_role_enum_members(self):
        """Test role enum has expected members"""
        from src.models.user import RoleEnum

        roles = [r.value for r in RoleEnum]
        assert 'guest' in roles
        assert 'admin' in roles
        assert 'sysadmin' in roles
        assert len(roles) == 3


class TestPasswordService:
    """Test password service"""

    def test_password_validation_too_short(self):
        """Test password too short"""
        from src.services.password_service import PasswordService

        result = PasswordService.validate_password_strength('Short1')
        assert not result['is_valid']
        assert any('8 characters' in err for err in result['errors'])

    def test_password_validation_no_uppercase(self):
        """Test password without uppercase"""
        from src.services.password_service import PasswordService

        result = PasswordService.validate_password_strength('lowercase123')
        assert not result['is_valid']
        assert any('uppercase' in err for err in result['errors'])

    def test_password_validation_no_lowercase(self):
        """Test password without lowercase"""
        from src.services.password_service import PasswordService

        result = PasswordService.validate_password_strength('UPPERCASE123')
        assert not result['is_valid']
        assert any('lowercase' in err for err in result['errors'])

    def test_password_validation_no_digit(self):
        """Test password without digit"""
        from src.services.password_service import PasswordService

        result = PasswordService.validate_password_strength('NoDigitsHere')
        assert not result['is_valid']
        assert any('number' in err for err in result['errors'])

    def test_password_validation_contains_email(self):
        """Test password contains email"""
        from src.services.password_service import PasswordService

        result = PasswordService.validate_password_strength(
            'test@example.com123',
            'test@example.com'
        )
        assert not result['is_valid']
        assert any('email' in err for err in result['errors'])

    def test_password_validation_valid(self):
        """Test valid password"""
        from src.services.password_service import PasswordService

        result = PasswordService.validate_password_strength('ValidPass123')
        assert result['is_valid']
        assert len(result['errors']) == 0

    def test_password_hash_and_verify(self):
        """Test password hashing and verification"""
        from src.services.password_service import PasswordService

        password = 'TestPassword123'
        password_hash = PasswordService.hash_password(password)

        # Hash should be different from password
        assert password_hash != password

        # Should verify correctly
        assert PasswordService.verify_password(password_hash, password)

        # Should not verify with wrong password
        assert not PasswordService.verify_password(password_hash, 'WrongPassword123')


class TestTokenService:
    """Test token service"""

    def test_generate_random_token(self):
        """Test random token generation"""
        from src.services.token_service import TokenService

        token1 = TokenService.generate_random_token()
        token2 = TokenService.generate_random_token()

        # Tokens should be different
        assert token1 != token2

        # Tokens should be URL-safe
        assert len(token1) > 0
        assert isinstance(token1, str)

    def test_hash_token(self):
        """Test token hashing"""
        from src.services.token_service import TokenService

        token = 'test-token-123'
        hash1 = TokenService.hash_token(token)
        hash2 = TokenService.hash_token(token)

        # Same token should produce same hash
        assert hash1 == hash2

        # Hash should be hex string (SHA-256 = 64 chars)
        assert len(hash1) == 64
        assert all(c in '0123456789abcdef' for c in hash1)

    def test_hash_different_tokens(self):
        """Test hashing different tokens"""
        from src.services.token_service import TokenService

        hash1 = TokenService.hash_token('token1')
        hash2 = TokenService.hash_token('token2')

        # Different tokens should produce different hashes
        assert hash1 != hash2


class TestTodoModelLogic:
    """Test todo model methods without database"""

    def test_todo_to_dict(self):
        """Test todo to_dict method"""
        from src.models.todo import Todo, PriorityEnum

        # Create a mock todo
        todo = Todo()
        todo.id = uuid.uuid4()
        todo.owner_id = uuid.uuid4()
        todo.description = 'Test todo'
        todo.due_date = datetime.utcnow() + timedelta(days=7)
        todo.priority = PriorityEnum.high
        todo.created_at = datetime.utcnow()
        todo.updated_at = datetime.utcnow()

        # Convert to dict
        data = todo.to_dict(include_owner_info=False)

        assert data['description'] == 'Test todo'
        assert data['priority'] == 'high'
        assert 'id' in data
        assert 'ownerId' in data
        assert 'dueDate' in data
        assert 'createdAt' in data
        assert 'updatedAt' in data


class TestUserModelLogic:
    """Test user model methods without database"""

    def test_user_to_dict(self):
        """Test user to_dict method"""
        from src.models.user import User, RoleEnum

        # Create a mock user
        user = User()
        user.id = uuid.uuid4()
        user.email = 'test@example.com'
        user.full_name = 'Test User'
        user.role = RoleEnum.guest
        user.email_verified_at = datetime.utcnow()
        user.created_at = datetime.utcnow()
        user.updated_at = datetime.utcnow()

        # Convert to dict
        data = user.to_dict()

        assert data['email'] == 'test@example.com'
        assert data['fullName'] == 'Test User'
        assert data['role'] == 'guest'
        assert data['emailVerified'] == True
        assert 'id' in data
        assert 'createdAt' in data
        assert 'updatedAt' in data

    def test_user_to_dict_unverified(self):
        """Test user to_dict with unverified email"""
        from src.models.user import User, RoleEnum

        user = User()
        user.id = uuid.uuid4()
        user.email = 'test@example.com'
        user.full_name = 'Test User'
        user.role = RoleEnum.guest
        user.email_verified_at = None  # Not verified
        user.created_at = datetime.utcnow()
        user.updated_at = datetime.utcnow()

        data = user.to_dict()
        assert data['emailVerified'] == False
