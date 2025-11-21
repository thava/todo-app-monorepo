"""Unit tests for JWT service."""

import uuid
from datetime import datetime, timedelta

import jwt
import pytest

from app.core.config import settings
from app.models.user import RoleEnum
from app.services.jwt import JWTService


class TestJWTService:
    """Test JWT service."""

    @pytest.fixture
    def jwt_service(self) -> JWTService:
        """Create JWT service instance."""
        return JWTService()

    @pytest.fixture
    def test_user_id(self) -> uuid.UUID:
        """Create test user ID."""
        return uuid.uuid4()

    def test_generate_access_token(self, jwt_service: JWTService, test_user_id: uuid.UUID) -> None:
        """Test access token generation."""
        email = "test@example.com"
        role = RoleEnum.GUEST

        token = jwt_service.generate_access_token(test_user_id, email, role)

        assert isinstance(token, str)
        assert len(token) > 0

        # Decode and verify payload
        payload = jwt.decode(token, settings.JWT_ACCESS_SECRET, algorithms=["HS256"])
        assert payload["sub"] == str(test_user_id)
        assert payload["email"] == email
        assert payload["role"] == role.value

    def test_generate_refresh_token(self, jwt_service: JWTService, test_user_id: uuid.UUID) -> None:
        """Test refresh token generation."""
        session_id = uuid.uuid4()

        token = jwt_service.generate_refresh_token(test_user_id, session_id)

        assert isinstance(token, str)
        assert len(token) > 0

        # Decode and verify payload
        payload = jwt.decode(token, settings.JWT_REFRESH_SECRET, algorithms=["HS256"])
        assert payload["sub"] == str(test_user_id)
        assert payload["sessionId"] == str(session_id)

    def test_verify_access_token_success(
        self, jwt_service: JWTService, test_user_id: uuid.UUID
    ) -> None:
        """Test access token verification with valid token."""
        email = "test@example.com"
        role = RoleEnum.ADMIN

        token = jwt_service.generate_access_token(test_user_id, email, role)
        payload = jwt_service.verify_access_token(token)

        assert payload is not None
        assert payload["sub"] == str(test_user_id)
        assert payload["email"] == email
        assert payload["role"] == role.value

    def test_verify_access_token_expired(self, jwt_service: JWTService, test_user_id: uuid.UUID) -> None:
        """Test access token verification with expired token."""
        # Create expired token manually
        now = datetime.utcnow()
        payload = {
            "sub": str(test_user_id),
            "email": "test@example.com",
            "role": RoleEnum.GUEST.value,
            "iat": now - timedelta(hours=2),
            "exp": now - timedelta(hours=1),
        }
        expired_token = jwt.encode(payload, settings.JWT_ACCESS_SECRET, algorithm="HS256")

        with pytest.raises(jwt.ExpiredSignatureError):
            jwt_service.verify_access_token(expired_token)

    def test_verify_access_token_invalid_signature(self, jwt_service: JWTService) -> None:
        """Test access token verification with invalid signature."""
        # Create token with wrong secret
        payload = {
            "sub": str(uuid.uuid4()),
            "email": "test@example.com",
            "role": RoleEnum.GUEST.value,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(minutes=15),
        }
        invalid_token = jwt.encode(payload, "wrong_secret", algorithm="HS256")

        with pytest.raises(jwt.InvalidSignatureError):
            jwt_service.verify_access_token(invalid_token)

    def test_verify_refresh_token_success(
        self, jwt_service: JWTService, test_user_id: uuid.UUID
    ) -> None:
        """Test refresh token verification with valid token."""
        session_id = uuid.uuid4()

        token = jwt_service.generate_refresh_token(test_user_id, session_id)
        payload = jwt_service.verify_refresh_token(token)

        assert payload is not None
        assert payload["sub"] == str(test_user_id)
        assert payload["sessionId"] == str(session_id)

    def test_verify_refresh_token_expired(self, jwt_service: JWTService, test_user_id: uuid.UUID) -> None:
        """Test refresh token verification with expired token."""
        # Create expired token manually
        now = datetime.utcnow()
        payload = {
            "sub": str(test_user_id),
            "sessionId": str(uuid.uuid4()),
            "iat": now - timedelta(days=8),
            "exp": now - timedelta(days=1),
        }
        expired_token = jwt.encode(payload, settings.JWT_REFRESH_SECRET, algorithm="HS256")

        with pytest.raises(jwt.ExpiredSignatureError):
            jwt_service.verify_refresh_token(expired_token)

    def test_access_token_different_roles(self, jwt_service: JWTService, test_user_id: uuid.UUID) -> None:
        """Test access token generation with different roles."""
        email = "test@example.com"

        for role in [RoleEnum.GUEST, RoleEnum.ADMIN, RoleEnum.SYSADMIN]:
            token = jwt_service.generate_access_token(test_user_id, email, role)
            payload = jwt_service.verify_access_token(token)

            assert payload is not None
            assert payload["role"] == role.value

    def test_token_contains_timestamps(self, jwt_service: JWTService, test_user_id: uuid.UUID) -> None:
        """Test that tokens contain iat and exp timestamps."""
        token = jwt_service.generate_access_token(test_user_id, "test@example.com", RoleEnum.GUEST)
        payload = jwt_service.verify_access_token(token)

        assert payload is not None
        assert "iat" in payload
        assert "exp" in payload
        assert payload["exp"] > payload["iat"]
