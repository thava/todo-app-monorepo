"""Password hashing and validation service"""
import bcrypt
import re


class PasswordService:
    """Service for password operations"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(password_hash: str, password: str) -> bool:
        """Verify a password against a hash"""
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8')
            )
        except Exception:
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
