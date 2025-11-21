"""Unit tests for password service."""


from app.services.password import PasswordService


class TestPasswordService:
    """Test password service."""

    def test_hash_password(self, password_service: PasswordService) -> None:
        """Test password hashing."""
        password = "TestPassword123!"
        hashed = password_service.hash_password(password)

        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$argon2")

    def test_verify_password_success(self, password_service: PasswordService) -> None:
        """Test password verification with correct password."""
        password = "TestPassword123!"
        hashed = password_service.hash_password(password)

        result = password_service.verify_password(hashed, password)
        assert result is True

    def test_verify_password_failure(self, password_service: PasswordService) -> None:
        """Test password verification with incorrect password."""
        password = "TestPassword123!"
        wrong_password = "WrongPassword456!"
        hashed = password_service.hash_password(password)

        result = password_service.verify_password(hashed, wrong_password)
        assert result is False

    def test_hash_password_different_results(self, password_service: PasswordService) -> None:
        """Test that hashing same password twice produces different results."""
        password = "TestPassword123!"
        hashed1 = password_service.hash_password(password)
        hashed2 = password_service.hash_password(password)

        # Hashes should be different due to random salt
        assert hashed1 != hashed2
        # But both should verify successfully
        assert password_service.verify_password(hashed1, password) is True
        assert password_service.verify_password(hashed2, password) is True

    def test_verify_password_empty_string(self, password_service: PasswordService) -> None:
        """Test password verification with empty password."""
        password = "TestPassword123!"
        hashed = password_service.hash_password(password)

        result = password_service.verify_password(hashed, "")
        assert result is False

    def test_hash_empty_password(self, password_service: PasswordService) -> None:
        """Test hashing empty password."""
        hashed = password_service.hash_password("")
        assert len(hashed) > 0
        assert password_service.verify_password(hashed, "") is True
