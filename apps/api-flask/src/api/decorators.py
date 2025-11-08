"""Custom decorators"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from ..models.user import User, RoleEnum
from ..app import db


def jwt_required_with_user(fn):
    """Decorator that provides the current user object"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 401
        return fn(user, *args, **kwargs)
    return wrapper


def role_required(*allowed_roles):
    """Decorator that checks if user has required role"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(user, *args, **kwargs):
            # Convert string roles to RoleEnum
            role_enums = [RoleEnum[role] if isinstance(role, str) else role for role in allowed_roles]
            if user.role not in role_enums:
                return jsonify({'message': 'Insufficient permissions'}), 403
            return fn(user, *args, **kwargs)
        return wrapper
    return decorator
