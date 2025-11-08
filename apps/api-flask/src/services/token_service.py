"""Token generation and validation service"""
import hashlib
import secrets
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token, create_refresh_token
from flask import current_app
import jwt as pyjwt


class TokenService:
    """Service for token operations"""

    @staticmethod
    def generate_access_token(identity: str, additional_claims: dict = None) -> str:
        """Generate JWT access token using JWT_ACCESS_SECRET"""
        return create_access_token(
            identity=identity,
            additional_claims=additional_claims or {}
        )

    @staticmethod
    def generate_refresh_token(identity: str, additional_claims: dict = None) -> str:
        """Generate JWT refresh token using JWT_REFRESH_SECRET"""
        # Flask-JWT-Extended doesn't support separate refresh secret out of the box
        # So we manually create the refresh token with the refresh secret
        expires_delta = current_app.config['JWT_REFRESH_TOKEN_EXPIRES']
        expires = datetime.utcnow() + expires_delta

        payload = {
            'sub': identity,
            'exp': expires,
            'type': 'refresh',
            'iat': datetime.utcnow(),
            **(additional_claims or {})
        }

        # Use the refresh secret
        refresh_secret = current_app.config['JWT_REFRESH_SECRET_KEY']
        return pyjwt.encode(payload, refresh_secret, algorithm='HS256')

    @staticmethod
    def verify_refresh_token(token: str) -> dict:
        """Verify and decode refresh token using JWT_REFRESH_SECRET"""
        try:
            refresh_secret = current_app.config['JWT_REFRESH_SECRET_KEY']
            payload = pyjwt.decode(token, refresh_secret, algorithms=['HS256'])
            return payload
        except pyjwt.ExpiredSignatureError:
            raise ValueError('Refresh token has expired')
        except pyjwt.InvalidTokenError:
            raise ValueError('Invalid refresh token')

    @staticmethod
    def generate_random_token() -> str:
        """Generate a random token (32 bytes, base64url)"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_token(token: str) -> str:
        """Hash a token using SHA-256"""
        return hashlib.sha256(token.encode('utf-8')).hexdigest()
