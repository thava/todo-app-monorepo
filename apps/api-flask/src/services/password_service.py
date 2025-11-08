"""Password hashing and validation service"""
from argon2 import PasswordHasher, Type
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
import re


class PasswordService:
    """Service for password operations"""

    # Argon2id parameters matching NestJS (@node-rs/argon2)
    # memoryCost: 19456 (19 MiB), timeCost: 2, parallelism: 1
    _ph = PasswordHasher(
        time_cost=2,           # timeCost
        memory_cost=19456,     # memoryCost (in KiB)
        parallelism=1,         # parallelism
        hash_len=32,           # Default hash length
        salt_len=16,           # Default salt length
        type=Type.ID           # Argon2id
    )

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using Argon2id"""
        return PasswordService._ph.hash(password)

    @staticmethod
    def verify_password(password_hash: str, password: str) -> bool:
        """Verify a password against a hash"""
        try:
            PasswordService._ph.verify(password_hash, password)
            return True
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            return False

    @staticmethod
    def validate_password_strength(password: str, email: str = None) -> dict:
        """
        Validate password strength
        Returns dict with 'is_valid' and 'errors' keys
        """
        errors = []

        # Minimum length
        if len(password) < 8:
            errors.append('Password must be at least 8 characters long')

        # Maximum length
        if len(password) > 128:
            errors.append('Password must be at most 128 characters long')

        # Must contain at least one lowercase letter
        if not re.search(r'[a-z]', password):
            errors.append('Password must contain at least one lowercase letter')

        # Must contain at least one uppercase letter
        if not re.search(r'[A-Z]', password):
            errors.append('Password must contain at least one uppercase letter')

        # Must contain at least one digit
        if not re.search(r'\d', password):
            errors.append('Password must contain at least one number')

        # Check if password contains email (if provided)
        if email and email.lower() in password.lower():
            errors.append('Password must not contain your email address')

        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }
