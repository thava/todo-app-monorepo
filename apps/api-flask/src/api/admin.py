"""Admin endpoints"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from marshmallow import Schema, fields, validate

from ..app import db
from ..models.user import User, RoleEnum
from ..services import PasswordService
from ..api.decorators import jwt_required_with_user, role_required

admin_bp = Blueprint('admin', __name__)


# Schemas
class UpdateUserSchema(Schema):
    email = fields.Email()
    password = fields.Str(validate=validate.Length(min=8, max=128))
    fullName = fields.Str(validate=validate.Length(min=1, max=255))
    role = fields.Str(validate=validate.OneOf(['guest', 'admin', 'sysadmin']))
    emailVerifiedAt = fields.DateTime(allow_none=True)


@admin_bp.route('/users', methods=['GET'])
@jwt_required_with_user
@role_required('admin', 'sysadmin')
def get_all_users(user):
    """Get all users (admin/sysadmin only)"""
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([u.to_dict() for u in users])


@admin_bp.route('/users/<uuid:user_id>', methods=['GET'])
@jwt_required_with_user
@role_required('admin', 'sysadmin')
def get_user_by_id(user, user_id):
    """Get user by ID (admin/sysadmin only)"""
    target_user = db.session.get(User, user_id)

    if not target_user:
        return jsonify({'message': 'User not found'}), 404

    return jsonify(target_user.to_dict())


@admin_bp.route('/users/<uuid:user_id>', methods=['PATCH'])
@jwt_required_with_user
@role_required('sysadmin')
def update_user(user, user_id):
    """Update user (sysadmin only)"""
    target_user = db.session.get(User, user_id)

    if not target_user:
        return jsonify({'message': 'User not found'}), 404

    data = UpdateUserSchema().load(request.json)

    # Update fields
    if 'email' in data:
        # Check if email already exists
        existing = User.query.filter(User.email == data['email'], User.id != user_id).first()
        if existing:
            return jsonify({'message': 'Email already exists'}), 400
        target_user.email = data['email']

    if 'password' in data:
        # Validate password
        password_validation = PasswordService.validate_password_strength(
            data['password'],
            target_user.email
        )
        if not password_validation['is_valid']:
            return jsonify({
                'message': 'Password does not meet security requirements',
                'errors': password_validation['errors']
            }), 400
        target_user.password_hash_primary = PasswordService.hash_password(data['password'])

    if 'fullName' in data:
        target_user.full_name = data['fullName']

    if 'role' in data:
        target_user.role = RoleEnum[data['role']]

    if 'emailVerifiedAt' in data:
        target_user.email_verified_at = data['emailVerifiedAt']

    target_user.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify(target_user.to_dict())


@admin_bp.route('/users/<uuid:user_id>', methods=['DELETE'])
@jwt_required_with_user
@role_required('sysadmin')
def delete_user(user, user_id):
    """Delete user (sysadmin only)"""
    target_user = db.session.get(User, user_id)

    if not target_user:
        return jsonify({'message': 'User not found'}), 404

    db.session.delete(target_user)
    db.session.commit()

    return '', 204
