"""Password hashing and validation service using Argon2."""

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


class PasswordService:
    """Service for password hashing and validation using Argon2."""

    def __init__(self) -> None:
        """Initialize password hasher with secure defaults."""
        self.hasher = PasswordHasher()

    def hash_password(self, password: str) -> str:
        """
        Hash a password using Argon2.

        Args:
            password: Plain text password to hash

        Returns:
            Hashed password string
        """
        return self.hasher.hash(password)

    def verify_password(self, password_hash: str, password: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            password_hash: The hashed password
            password: Plain text password to verify

        Returns:
            True if password matches, False otherwise
        """
        try:
            self.hasher.verify(password_hash, password)
            # Check if hash needs rehashing (e.g., parameters changed)
            if self.hasher.check_needs_rehash(password_hash):
                # In a real application, you might want to rehash the password here
                pass
            return True
        except VerifyMismatchError:
            return False

    def validate_password_strength(
        self, password: str, email: str | None = None
    ) -> dict[str, bool | list[str]]:
        """
        Validate password strength.

        Args:
            password: Password to validate
            email: User's email (to check if password contains email)

        Returns:
            Dictionary with validation results
        """
        errors: list[str] = []

        # Minimum length
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")

        # Maximum length
        if len(password) > 128:
            errors.append("Password must be at most 128 characters long")

        # Check if password contains email
        if email and email.lower() in password.lower():
            errors.append("Password cannot contain your email address")

        # Check for common weak passwords
        weak_passwords = ["password", "12345678", "qwerty", "abc123"]
        if password.lower() in weak_passwords:
            errors.append("Password is too common")

        return {
            "isValid": len(errors) == 0,
            "errors": errors,
        }
